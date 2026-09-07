"""Failure analysis — turns evaluation history into better selection.

The loop: task → execution → evaluation → performance history → failure
analysis → better agent/model/capability selection. This module reads
persisted evaluation records and produces:

* persistent failure categories (with counts and trends),
* recommendations (route to stronger tier, add retries, fix config, …),
* a best-match answer for "who should do this kind of task" combining
  pass rate, cost and latency — used by delegation and dynamic planning.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from agentos.domain.models import EvaluationRecord

_WORD_RE = re.compile(r"[a-z0-9]+")

# task-class keywords → relevant capability ids (from the skill registry)
_TASK_CLASSES: list[tuple[tuple[str, ...], list[str]]] = [
    (("landing", "website", "frontend", "ui", "page", "react", "next"),
     ["frontend-engineering", "react-nextjs", "ui-design", "design-quality"]),
    (("api", "backend", "server", "database", "service"),
     ["backend-engineering", "api-design", "database-design"]),
    (("research", "market", "validate", "demand", "competitor"),
     ["market-research", "competitor-analysis", "evidence-synthesis"]),
    (("security", "audit", "secrets", "threat"),
     ["security-review", "threat-modeling", "secret-scanning"]),
    (("test", "testing", "regression", "quality"),
     ["testing", "test-automation", "e2e-testing"]),
    (("marketing", "seo", "content", "copy", "campaign"),
     ["seo", "copywriting", "content-strategy"]),
    (("sales", "lead", "outreach", "pipeline"),
     ["lead-research", "outreach-drafting", "sales-strategy"]),
]


def failure_summary(records: list[EvaluationRecord]) -> dict[str, Any]:
    """Persistent failure categories across all recorded runs."""
    classes: dict[str, int] = {}
    by_agent: dict[str, dict[str, int]] = {}
    for r in records:
        if r.passed:
            continue
        cls = r.fail_class or "quality"
        classes[cls] = classes.get(cls, 0) + 1
        if r.agent_id:
            bucket = by_agent.setdefault(r.agent_id, {})
            bucket[cls] = bucket.get(cls, 0) + 1
    return {"total_failed": sum(classes.values()),
            "by_class": classes,
            "by_agent": by_agent}


def recommendations(records: list[EvaluationRecord]) -> list[str]:
    classes = failure_summary(records)["by_class"]
    out: list[str] = []
    if classes.get("transient", 0) >= 2:
        out.append("recurring transient failures — raise retry budget or add model failover")
    if classes.get("configuration", 0) >= 1:
        out.append("configuration failures — check provider keys and adapter setup")
    if classes.get("permission", 0) >= 1:
        out.append("permission denials — review tool permission policies")
    if (classes.get("logic", 0) + classes.get("quality", 0)) >= 2:
        out.append("logic/quality failures — route these task classes to a stronger model tier")
    if not out:
        out.append("no systematic failures detected")
    return out


def classify_task(goal: str) -> tuple[str, list[str]]:
    """Map a goal to (task_class, recommended capability ids)."""
    low = goal.lower()
    for keywords, caps in _TASK_CLASSES:
        if any(k in low for k in keywords):
            return keywords[0], caps
    return "general", []


def best_match(records: list[EvaluationRecord], goal: str,
               limit: int = 3) -> dict[str, Any]:
    """Answer 'who does this best?' for a goal, from evaluation history.

    Ranks candidates by (pass_rate, avg_score, -avg_cost, -avg_latency) and
    only trusts records with enough samples; otherwise suggests evidence-free
    default routing. Includes model + capability suggestions.
    """
    task_class, capabilities = classify_task(goal)
    by_agent: dict[str, list[EvaluationRecord]] = {}
    for r in records:
        if r.agent_id:
            by_agent.setdefault(r.agent_id, []).append(r)
    ranked = []
    for agent_id, rs in by_agent.items():
        if not rs:
            continue
        passed = sum(1 for r in rs if r.passed)
        ranked.append({
            "agent_id": agent_id,
            "runs": len(rs),
            "pass_rate": round(passed / len(rs), 3),
            "avg_score": round(sum(r.score for r in rs) / len(rs), 2),
            "avg_cost": round(sum(r.cost for r in rs) / len(rs), 5),
            "avg_latency_ms": round(sum(r.latency_ms for r in rs) / len(rs), 1),
        })
    ranked.sort(key=lambda r: (r["pass_rate"], r["avg_score"], -r["avg_cost"],
                               -r["avg_latency_ms"]), reverse=True)
    top = ranked[:limit]
    trusted = [r for r in top if r["runs"] >= 2]
    return {
        "task_class": task_class,
        "recommended_capabilities": capabilities,
        "candidates": top,
        "recommended_agent": trusted[0]["agent_id"] if trusted else None,
        "note": ("based on evaluation history" if trusted else
                 "insufficient history — use default routing"),
    }


async def analyze_svc(svc: Any, goal: str = "") -> dict[str, Any]:
    """Convenience: read persisted records and produce the full analysis."""
    records = [EvaluationRecord.model_validate(r)
               for r in await svc.entity_store.list_docs("evaluation")]
    analysis = {
        "failure_summary": failure_summary(records),
        "recommendations": recommendations(records),
    }
    if goal:
        analysis["best_match"] = best_match(records, goal)
    return analysis