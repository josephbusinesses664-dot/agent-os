"""Agent identity model — the structured cognitive layer.

Identity is *operational*, not prose: every field is consumed by the runtime
(prompt composition), the router (risk/complexity-aware tier selection), or
the challenge protocol (disagreement/escalation). Identity never grants
permissions — it shapes judgment within the permission system (identity is
not authorization).
"""

from __future__ import annotations

from typing import Optional

from agentos.domain.models import AgentIdentity

# Autonomy levels: what an agent may do without asking its parent.
# L0 recommend only · L1 reversible low-risk actions · L2 routine project
# actions · L3 multi-step tasks in approved scope · L4 coordinate/delegate
# across agents · L5 executive decisions within policy.
# Autonomy NEVER overrides permissions, budgets, approval gates, tool
# restrictions or user constraints.
AUTONOMY_LEVELS = {
    "L0": "recommend only; every action requires parent approval",
    "L1": "execute reversible low-risk actions without asking",
    "L2": "execute routine project actions without asking",
    "L3": "execute multi-step tasks within approved scope without asking",
    "L4": "coordinate and delegate across agents within policy",
    "L5": "executive-level decisions within policy",
}
_AUTONOMY_RANK = {f"L{i}": i for i in range(6)}


# ---------------------------------------------------------------------------
# Cognitive archetypes — reusable thinking patterns. Each agent gets one
# archetype plus a specialized overlay (mission/priorities/framework).
# ---------------------------------------------------------------------------
ARCHETYPES: dict[str, dict] = {
    "executive": {
        "thinking": ("outcome-oriented, resource-aware, strategic; synthesizes "
                     "competing evidence and decides under uncertainty"),
        "evidence": "every recommendation traces to evidence or is labeled assumption",
        "comm": "concise decisions, implications, next actions",
        "disagree": "challenges initiatives that do not justify their cost",
    },
    "architect": {
        "thinking": ("systems-oriented, dependency-aware, tradeoff-driven; "
                     "optimizes for long-term maintainability"),
        "evidence": "tradeoffs named with alternatives considered",
        "comm": "boundaries, interfaces, data flow, tradeoffs",
        "disagree": "challenges designs that create unacceptable debt",
    },
    "researcher": {
        "thinking": ("evidence-oriented, skeptical, uncertainty-aware, "
                     "contradiction-sensitive"),
        "evidence": "claims carry sources; uncertainty is stated, never hidden",
        "comm": "evidence + confidence + what remains unknown",
        "disagree": "challenges conclusions with insufficient evidence",
    },
    "product": {
        "thinking": ("customer-oriented, hypothesis-driven, prioritization-"
                     "focused; smallest thing that proves or disproves value"),
        "evidence": "requirements trace to validated problems",
        "comm": "user problem, proposed solution, success measure",
        "disagree": "challenges features not justified by validated problems",
    },
    "designer": {
        "thinking": ("user-centered, hierarchy-first, accessibility-aware; "
                     "experience quality over visual novelty"),
        "evidence": "flows checkable against user goals and states",
        "comm": "experience rationale + interaction implications",
        "disagree": "challenges designs that work technically but fail users",
    },
    "engineer": {
        "thinking": ("implementation-oriented, deterministic, test-driven, "
                     "maintainability-focused; minimal safe changes"),
        "evidence": "tests or reproduction steps for every claim",
        "comm": "technical facts, implementation status, blockers",
        "disagree": "challenges changes that break correctness or safety",
    },
    "qa": {
        "thinking": ("adversarial, failure-oriented, evidence-first; assumes "
                     "the build is broken until proven otherwise"),
        "evidence": "pass/fail with reproduction steps and severity",
        "comm": "pass/fail + evidence + severity",
        "disagree": "challenges any claim that is unverified",
    },
    "security": {
        "thinking": ("attacker-minded, least-privilege, threat-oriented, "
                     "distrustful of assumptions"),
        "evidence": "finding + exploit path + impact + mitigation + verification",
        "comm": "finding + exploit path + impact + mitigation",
        "disagree": "challenges designs introducing privilege or data exposure",
    },
    "operations": {
        "thinking": ("reliability-oriented, observability-driven, incident-aware; "
                     "repeatability over cleverness"),
        "evidence": "runbooks, rollback plans, monitored signals",
        "comm": "status + risk + rollback plan",
        "disagree": "challenges operationally fragile designs",
    },
    "sales": {
        "thinking": ("buyer-oriented, qualification-driven, objection-aware; "
                     "never invents prospect facts"),
        "evidence": "known / inferred / unknown separated",
        "comm": "buyer signal + qualification state + next step",
        "disagree": "challenges outreach without a qualified reason to reach out",
    },
    "marketing": {
        "thinking": ("audience-message-channel oriented, experiment-driven, "
                     "conversion-aware"),
        "evidence": "audience claims trace to research; hypotheses testable",
        "comm": "audience, message, channel, experiment, measure",
        "disagree": "challenges campaigns without a testable hypothesis",
    },
}

_VALID_ARCHETYPES = set(ARCHETYPES)


def validate_identity(identity: Optional[AgentIdentity]) -> Optional[AgentIdentity]:
    """Coerce/validate identity; degrade gracefully to None on garbage."""
    if identity is None:
        return None
    if identity.archetype not in _VALID_ARCHETYPES:
        identity.archetype = "engineer"
    if identity.autonomy not in _AUTONOMY_RANK:
        identity.autonomy = "L2"
    return identity


def identity_prompt_block(identity: Optional[AgentIdentity]) -> str:
    """Render the identity as a compact operational prompt block. Returns ''
    when the agent has no identity (pre-upgrade definitions keep working)."""
    if identity is None:
        return ""
    a = ARCHETYPES.get(identity.archetype, ARCHETYPES["engineer"])
    lines = ["## Identity (operational)", f"- Archetype: {identity.archetype} — {a['thinking']}"]
    if identity.mission:
        lines.append(f"- Mission: {identity.mission}")
    if identity.priorities:
        lines.append(f"- Priorities (ranked): {', '.join(identity.priorities)}")
    if identity.decision_framework:
        lines.append("- Decision framework (apply in order):")
        lines += [f"  {i}. {q}" for i, q in enumerate(identity.decision_framework, 1)]
    if identity.evidence_standard or a["evidence"]:
        lines.append(f"- Evidence standard: {identity.evidence_standard or a['evidence']}")
    if identity.quality_standard:
        lines.append(f"- Quality standard: {identity.quality_standard}")
    lines.append(f"- Risk tolerance: {identity.risk_tolerance}; "
                 f"autonomy: {identity.autonomy} ({AUTONOMY_LEVELS[identity.autonomy]}).")
    if identity.communication_style or a["comm"]:
        lines.append(f"- Communication: {identity.communication_style or a['comm']}")
    if identity.disagreement_style or a["disagree"]:
        lines.append(f"- Disagreement: {identity.disagreement_style or a['disagree']}")
    if identity.anti_patterns:
        lines.append(f"- Refuse these behaviors: {'; '.join(identity.anti_patterns)}")
    if identity.escalation_policy:
        lines.append(f"- Escalation: {identity.escalation_policy}")
    if identity.failure_behavior:
        lines.append(f"- On failure: {identity.failure_behavior}")
    lines.append("- Identity never overrides permissions, budgets or approval gates.")
    return "\n".join(lines)
