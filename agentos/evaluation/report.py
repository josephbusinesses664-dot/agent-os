"""Evaluation reports: leaderboard + trajectory analysis.

Answers the operational question "which agent/model/skill/workflow performs
best for this kind of task?" from persisted evaluation records and traces.
"""

from __future__ import annotations

from typing import Any, Optional

from agentos.domain.models import EvaluationRecord

_ORDER = ["t3", "t2", "t1", "t0"]


def _agg(records: list[EvaluationRecord], key: str) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[EvaluationRecord]] = {}
    for r in records:
        value = getattr(r, key, None)
        if value:
            buckets.setdefault(value, []).append(r)
    out: dict[str, dict[str, float]] = {}
    for value, rs in buckets.items():
        passed = sum(1 for r in rs if r.passed)
        out[value] = {
            "runs": len(rs),
            "pass_rate": round(passed / len(rs), 3),
            "avg_score": round(sum(r.score for r in rs) / len(rs), 2),
            "avg_cost": round(sum(r.cost for r in rs) / len(rs), 5),
            "avg_latency_ms": round(sum(r.latency_ms for r in rs) / len(rs), 1),
        }
    return out


def leaderboard(records: list[EvaluationRecord], group_by: str = "agent_id",
                limit: int = 10) -> list[dict]:
    """Rank groups by pass_rate then avg_score (cost-aware)."""
    agg = _agg(records, group_by)
    rows = [{"key": k, **v} for k, v in agg.items()]
    rows.sort(key=lambda r: (r["pass_rate"], r["avg_score"], -r["avg_cost"]),
              reverse=True)
    return rows[:limit]


def cost_vs_quality(records: list[EvaluationRecord]) -> list[dict]:
    """Cost-vs-quality comparison per model: the input to routing decisions."""
    return leaderboard(records, group_by="model_id")


def trajectory_analysis(records: list[EvaluationRecord]) -> dict[str, Any]:
    """Failure categorization + recommendations from run records."""
    fail_classes: dict[str, int] = {}
    for r in records:
        if not r.passed and r.fail_class:
            fail_classes[r.fail_class] = fail_classes.get(r.fail_class, 0) + 1
        elif not r.passed and not r.fail_class:
            fail_classes["quality"] = fail_classes.get("quality", 0) + 1
    recommendations: list[str] = []
    if fail_classes.get("transient", 0) >= 2:
        recommendations.append("transient failures recurring — raise retry budget or add failover")
    if fail_classes.get("configuration", 0) >= 1:
        recommendations.append("configuration failures present — check API keys/provider setup")
    if fail_classes.get("logic", 0) >= 2 or fail_classes.get("quality", 0) >= 2:
        recommendations.append("quality/logic failures — route these task types to a stronger tier")
    if fail_classes.get("permission", 0) >= 1:
        recommendations.append("permission denials — review tool permission policies")
    return {"fail_classes": fail_classes,
            "total_failed": sum(fail_classes.values()),
            "recommendations": recommendations}


def best_for(records: list[EvaluationRecord], task_kind: str = "") -> dict[str, Any]:
    """One-line answer to 'who should do this work?' — used by the router's
    delegation advice when a group of agents can handle a task type."""
    rows = leaderboard(records, group_by="agent_id", limit=1)
    if not rows:
        return {"recommendation": "no evaluation data yet — use default routing"}
    top = rows[0]
    return {
        "agent_id": top["key"],
        "pass_rate": top["pass_rate"],
        "avg_score": top["avg_score"],
        "avg_cost": top["avg_cost"],
        "recommendation": (f"agent {top['key']} leads with "
                           f"{top['pass_rate']:.0%} pass rate, "
                           f"score {top['avg_score']}/5, "
                           f"${top['avg_cost']:.5f}/run"),
    }