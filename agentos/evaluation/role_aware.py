"""Role-aware performance evaluation (Phases 6/7 of the governance upgrade).

Workers, directors and executives are not measured by the same yardstick.
This module derives role-specific evaluation criteria from the EXISTING
archetype system (no parallel personality infra) and evaluates both:

- agent-level: which operational signals matter for this role
  (e.g. a QA agent is measured on verification behavior, an executive on
  delegation quality and evidence use)
- run-level: what a single AgentRunResult says about role-appropriate
  behavior (e.g. a researcher that reports uncertainty, a QA agent that
  verifies before approving)

Everything is computed from real recorded signals — no fabricated scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# Role-specific criteria per archetype: what operational signals matter.
ROLE_CRITERIA: dict[str, dict[str, str]] = {
    "executive": {
        "delegation_quality": "delegates rather than doing workers' jobs",
        "resource_discipline": "cost proportional to outcome",
        "risk_awareness": "high-risk actions gated, escalations appropriate",
        "evidence_use": "decisions reference evidence",
    },
    "architect": {
        "technical_risk_detection": "flags failure modes and debt",
        "verification": "architecture testable, alternatives recorded",
        "production_safety": "safety constraints named",
    },
    "researcher": {
        "evidence_quality": "claims carry sources",
        "uncertainty_honesty": "confidence stated; unknowns named",
        "source_diversity": "more than one independent source",
    },
    "product": {
        "customer_value_reasoning": "outcomes over features",
        "scope_discipline": "smallest valuable slice; out-of-scope named",
        "validation_quality": "requirements trace to evidence",
    },
    "designer": {
        "accessibility": "a11y states considered",
        "state_completeness": "loading/error/empty designed",
        "experience_rationale": "decisions justify UX impact",
    },
    "engineer": {
        "verification": "tests/evidence for claims",
        "minimal_change": "small safe diffs over rewrites",
        "failure_handling": "error paths addressed",
    },
    "qa": {
        "defect_discovery": "finds failures rather than approving",
        "verification_rigor": "no pass without evidence",
        "edge_case_coverage": "failure paths exercised",
    },
    "security": {
        "threat_identification": "exploit paths named",
        "least_privilege": "rejects over-privileged designs",
        "verification_rigor": "mitigations verified not assumed",
    },
    "operations": {
        "reliability": "rollback/monitoring present",
        "repeatability": "runbooks, no snowflakes",
        "incident_readiness": "signals and alerts wired",
    },
    "sales": {
        "qualification_honesty": "known/inferred/unknown split",
        "evidence_based": "prospect facts sourced",
    },
    "marketing": {
        "hypothesis_quality": "testable claims",
        "audience_evidence": "audience claims sourced",
    },
}


@dataclass
class RoleEvaluation:
    """Result of evaluating one run against role-specific criteria."""

    agent_id: str
    archetype: str
    criteria: dict[str, str] = field(default_factory=dict)   # criterion -> verdict text
    signals: dict[str, float] = field(default_factory=dict)  # measured signals
    score: float = 0.0        # 0..1 role-appropriate quality
    notes: list[str] = field(default_factory=list)


def _identity(agent: Any) -> Any:
    return getattr(agent, "identity", None)


def archetype_of(agent: Any) -> str:
    ident = _identity(agent)
    return ident.archetype if ident else "engineer"


def evaluate_run_role_aware(agent: Any, result: Any) -> RoleEvaluation:
    """Evaluate one AgentRunResult against the agent's role criteria.

    Measured signals (all real): verification behavior, honesty about
    failure, tool evidence, cost discipline, uncertainty language.
    """
    ident = _identity(agent)
    archetype = archetype_of(agent)
    criteria = ROLE_CRITERIA.get(archetype, ROLE_CRITERIA["engineer"])
    ev = RoleEvaluation(agent_id=agent.id, archetype=archetype,
                        criteria={k: v for k, v in criteria.items()})

    content = (getattr(result, "content", "") or "").lower()
    failed = bool(getattr(result, "error", None))
    verified = bool(getattr(result, "verified", False))
    tool_results = getattr(result, "tool_results", []) or []
    tool_calls = getattr(result, "tool_calls", []) or []
    cost = getattr(result, "cost", 0.0) or 0.0

    # ---- shared signals ---------------------------------------------------
    ev.signals["verified"] = 1.0 if verified else 0.0
    ev.signals["honest_failure"] = 1.0 if (failed and result.fail_class != "logic") else 0.0
    ev.signals["tool_evidence"] = 1.0 if any(r.get("ok") for r in tool_results) else (
        0.5 if tool_results else 0.0)
    ev.signals["uncertainty_language"] = 1.0 if any(
        w in content for w in ("uncertain", "insufficient evidence", "confidence",
                               "unverified", "unknown", "assumption")) else 0.0

    # ---- role weighting -----------------------------------------------------
    weights: dict[str, float] = {
        "verified": 0.25, "honest_failure": 0.15, "tool_evidence": 0.35,
        "uncertainty_language": 0.25,
    }
    if archetype == "qa":
        weights = {"verified": 0.45, "honest_failure": 0.15, "tool_evidence": 0.25,
                   "uncertainty_language": 0.15}
    elif archetype == "security":
        weights = {"verified": 0.4, "honest_failure": 0.2, "tool_evidence": 0.25,
                   "uncertainty_language": 0.15}
    elif archetype == "researcher":
        weights = {"verified": 0.1, "honest_failure": 0.2, "tool_evidence": 0.3,
                   "uncertainty_language": 0.4}
    elif archetype == "executive":
        # executives decide more than they execute; tool evidence matters less
        weights = {"verified": 0.05, "honest_failure": 0.25, "tool_evidence": 0.2,
                   "uncertainty_language": 0.5}
    score = sum(ev.signals[k] * w for k, w in weights.items())
    ev.score = round(min(score, 1.0), 3)

    # ---- notes --------------------------------------------------------------
    if archetype in ("qa", "security") and not verified and not failed:
        ev.notes.append("role expects verification before signoff; run not verified")
    if archetype == "researcher" and ev.signals["uncertainty_language"] == 0.0 and not failed:
        ev.notes.append("no confidence/uncertainty language in a research report")
    if failed and not getattr(result, "error", None):
        ev.notes.append("failed run without recorded error (honesty gap)")
    return ev


async def evaluate_agent_role_aware(performance: Any, agent: Any) -> dict:
    """Aggregate role-aware view over an agent's recorded performance stats.

    Returns criteria + the operational signals that matter for this role,
    with an explainable verdict. Uses only recorded observations."""
    archetype = archetype_of(agent)
    criteria = ROLE_CRITERIA.get(archetype, ROLE_CRITERIA["engineer"])
    stats = await performance.stats(agent.id)
    out: dict[str, Any] = {
        "agent_id": agent.id,
        "archetype": archetype,
        "criteria": criteria,
        "runs": stats.runs,
        "signals": {},
        "verdict": "",
    }
    if stats.runs == 0:
        out["verdict"] = "no recorded runs — no role evaluation yet"
        return out

    signals: dict[str, Any] = {
        "success_rate": stats.success_rate,
        "avg_review_score": stats.avg_review_score,
        "verification_pass_rate": (stats.evaluations_passed / stats.evaluations_total
                                   if stats.evaluations_total else None),
        "tool_efficiency": stats.tool_efficiency,
        "cost_discipline": stats.avg_cost,
        "downstream_rate": stats.downstream_rate if stats.downstream_total else None,
    }
    out["signals"] = signals

    # role-weighted verdict
    notes: list[str] = []
    if archetype in ("qa", "security"):
        if signals["verification_pass_rate"] is None:
            notes.append("no verification records yet — rigor unmeasured")
        elif signals["verification_pass_rate"] < 0.9:
            notes.append("verification pass rate below role bar (0.9)")
    if archetype == "executive":
        if stats.downstream_total >= 3:
            notes.append(f"delegation outcome rate {stats.downstream_rate:.0%} "
                         f"over {stats.downstream_total} delegations")
        else:
            notes.append("insufficient delegation history to judge allocation quality")
    if archetype == "researcher" and stats.avg_review_score:
        notes.append(f"evidence quality via review score {stats.avg_review_score:.2f}")
    out["verdict"] = "; ".join(notes) or "signals within role expectations"
    return out
