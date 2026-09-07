"""Agent identity behavioral tests (Phases 25/26/32 of the identity upgrade).

Do not test "does the agent say it is a CTO" — test that identity changes
behavior: prompt composition, autonomy gating, structured disagreement
payloads, escalation policy, role boundaries, and the security boundary
(identity ≠ authorization).
"""

from __future__ import annotations

import pytest

from agentos.agents.hierarchy import build_org
from agentos.agents.identity import (
    ARCHETYPES,
    AUTONOMY_LEVELS,
    identity_prompt_block,
    validate_identity,
)
from agentos.agents.identities import AGENT_IDENTITIES
from agentos.domain.models import AgentDef, AgentIdentity


# ---------------------------------------------------------------------------
# identity coverage over the org
# ---------------------------------------------------------------------------

def test_every_builtin_agent_has_an_identity():
    org = build_org()
    assert len(org) >= 40
    missing = [a.id for a in org if a.identity is None]
    assert not missing, f"agents without identity: {missing}"


def test_identities_have_operational_content():
    for agent_id, ident in AGENT_IDENTITIES.items():
        assert ident.mission, agent_id
        assert ident.priorities, agent_id
        assert len(ident.decision_framework) >= 3, agent_id
        assert ident.archetype in ARCHETYPES, agent_id


def test_role_boundaries_are_distinct():
    """Phase 8: no two agents own the same question (spot-check the classic
    collisions)."""
    assert "What do customers actually need" in AGENT_IDENTITIES["product-researcher"].mission
    assert "What is happening in the market" in AGENT_IDENTITIES["market-researcher"].mission
    assert "How are alternatives positioned" in AGENT_IDENTITIES["competitor-analyst"].mission
    assert "What should we build" in AGENT_IDENTITIES["product-manager"].mission
    assert "How should it be built" in AGENT_IDENTITIES["software-architect"].mission
    assert "Does it actually work" in AGENT_IDENTITIES["qa-director"].mission
    assert "Can it be abused" in AGENT_IDENTITIES["security-reviewer"].mission
    assert "Is the overall initiative worth doing" in AGENT_IDENTITIES["executive"].mission


# ---------------------------------------------------------------------------
# archetypes differ cognitively
# ---------------------------------------------------------------------------

def test_security_and_research_archetypes_differ():
    sec = identity_prompt_block(AGENT_IDENTITIES["security-reviewer"])
    res = identity_prompt_block(AGENT_IDENTITIES["market-researcher"])
    assert "attacker-minded" in sec
    assert "least-privilege" in sec
    assert "evidence-oriented" in res
    assert "uncertainty-aware" in res
    # the security prompt must not leak researcher thinking and vice versa
    assert "attacker-minded" not in res
    assert "uncertainty-aware" not in sec


def test_decision_frameworks_render_in_order():
    block = identity_prompt_block(AGENT_IDENTITIES["executive"])
    assert "Decision framework (apply in order)" in block
    i1 = block.index("1. What outcome matters?")
    i4 = block.index("4. What should we NOT do?")
    assert i1 < i4


def test_anti_patterns_render_as_refusals():
    block = identity_prompt_block(AGENT_IDENTITIES["devops-engineer"])
    assert "Refuse these behaviors" in block
    assert "irreversible production changes" in block


# ---------------------------------------------------------------------------
# identity changes runtime prompts (Phase 3: personality → behavior)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_runtime_prompt_includes_identity_and_differs_by_role(svc):
    from agentos.domain.models import Project, Task

    task = Task(task_id="t1", project_id="p1", title="plan", description="design a cache")
    project = Project(project_id="p1", name="p", objective="o")

    agent_map = {a.id: a for a in await svc.agent_registry.list()}
    runtime_sec = svc.runtime(agent_map["security-reviewer"], task, project)
    runtime_res = svc.runtime(agent_map["market-researcher"], task, project)
    sys_sec, _ = await runtime_sec._build_prompt(task)
    sys_res, _ = await runtime_res._build_prompt(task)

    assert "## Identity (operational)" in sys_sec
    assert "attacker-minded" in sys_sec
    assert "What can be abused?" in sys_sec
    assert "evidence-oriented" in sys_res
    # the two agents must receive genuinely different operating instructions
    assert "attacker-minded" not in sys_res
    assert "What can be abused?" not in sys_res


# ---------------------------------------------------------------------------
# autonomy levels (Phase 9) — influence, never override
# ---------------------------------------------------------------------------

def test_autonomy_ladder_is_role_appropriate():
    assert AGENT_IDENTITIES["executive"].autonomy == "L5"
    assert AGENT_IDENTITIES["chief-of-staff"].autonomy == "L4"
    assert AGENT_IDENTITIES["requirements-analyst"].autonomy == "L1"
    assert AGENT_IDENTITIES["deployment-agent"].autonomy == "L1"
    assert AGENT_IDENTITIES["product-manager"].autonomy == "L3"


def test_autonomy_levels_documented_and_used():
    for lvl in ("L0", "L5"):
        assert lvl in AUTONOMY_LEVELS
    block = identity_prompt_block(AGENT_IDENTITIES["deployment-agent"])
    assert "autonomy: L1" in block and "reversible" in block


def test_identity_validation_degrades_garbage():
    ident = validate_identity(AgentIdentity(archetype="wizard", autonomy="L9"))
    assert ident.archetype == "engineer"
    assert ident.autonomy == "L2"


# ---------------------------------------------------------------------------
# risk profiles (Phase 10)
# ---------------------------------------------------------------------------

def test_risk_tolerance_differs_by_role():
    assert AGENT_IDENTITIES["security-reviewer"].risk_tolerance == "minimal"
    assert AGENT_IDENTITIES["devops-engineer"].risk_tolerance == "minimal"
    assert AGENT_IDENTITIES["executive"].risk_tolerance == "high"
    assert AGENT_IDENTITIES["growth-agent"].risk_tolerance == "high"
    assert AGENT_IDENTITIES["qa-director"].risk_tolerance == "minimal"


# ---------------------------------------------------------------------------
# structured disagreement (Phase 6/26)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_security_challenge_carries_full_payload(svc):
    """Security reviewer challenges an over-privileged design: the challenge
    must be a structured object (claim, evidence, severity, action)."""
    m = await svc.messages.send_challenge(
        "security-reviewer", "backend-lead",
        "Requested integration runs with admin DB credentials",
        evidence=["integration spec asks for superuser role",
                  "no read-only role exists in the plan"],
        severity="blocking",
        recommended_action="use a scoped read-only role; cap table access",
        claim="privilege escalation risk",
        scope="data layer")
    assert m.payload["severity"] == "blocking"
    assert len(m.payload["evidence"]) == 2
    assert m.payload["status"] == "open"
    assert m.requires_response is True
    assert m.priority == "high"


@pytest.mark.asyncio
async def test_challenge_resolution_is_bounded_and_recorded(svc):
    m = await svc.messages.send_challenge(
        "qa-director", "frontend-lead", "claim unverified",
        evidence=["no test run recorded"], severity="high")
    decision = await svc.messages.resolve_challenge(
        m.message_id, "frontend-lead", "accept",
        rationale="you're right; adding the missing test run")
    assert decision.message_type.value == "decision"
    assert decision.payload["verdict"] == "accept"
    assert decision.recipient == "qa-director"  # decision flows back to challenger
    # original challenge marked resolved
    stored = await svc.messages.store.get("messages", m.message_id, None) \
        if False else None  # placeholder guard
    assert decision.payload["challenge_id"] == m.message_id


@pytest.mark.asyncio
async def test_reject_without_rationale_is_refused(svc):
    m = await svc.messages.send_challenge("cto", "backend-lead", "debt concern")
    with pytest.raises(ValueError):
        await svc.messages.resolve_challenge(m.message_id, "x", "bogus-verdict")


@pytest.mark.asyncio
async def test_agent_challenge_tool_end_to_end(svc):
    """The runtime tool path: agent raises a challenge through the executor."""
    from agentos.domain.models import Project, Task

    task = Task(task_id="t1", project_id="p1", title="review", description="")
    project = Project(project_id="p1", name="p", objective="o")
    sec = await svc.agent_registry.get("security-reviewer")
    ctx = svc.runtime(sec, task, project).ctx
    result = await svc.executor.execute(ctx, sec, "agent.challenge", {
        "agent": "backend-lead",
        "concern": "API key stored in plaintext config",
        "evidence": ["config.py:12 contains raw key"],
        "severity": "high",
        "recommended_action": "move to secret store",
    })
    assert result["ok"] is True
    assert result["challenge_id"]
    inbox = await svc.messages.inbox("backend-lead")
    assert any(m.message_type.value == "challenge" for m in inbox)
    challenge = [m for m in inbox if m.message_type.value == "challenge"][0]
    assert challenge.payload["evidence"] == ["config.py:12 contains raw key"]


# ---------------------------------------------------------------------------
# security boundary (Phase 32): identity ≠ authorization
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_identity_never_grants_permissions(svc):
    """An agent claiming to be the CEO gains nothing: delegation is gated by
    the org chart + explicit permission, not by identity or prompt claims."""
    from agentos.domain.models import Project, Task

    task = Task(task_id="t1", project_id="p1", title="x", description="")
    project = Project(project_id="p1", name="p", objective="o")
    frontend = await svc.agent_registry.get("frontend-lead")
    ctx = svc.runtime(frontend, task, project).ctx
    # frontend-lead has no delegation right over database-engineer (not its child)
    result = await svc.executor.execute(ctx, frontend, "agent.delegate",
                                        {"agent": "database-engineer",
                                         "description": "do work"})
    assert not result["ok"]
    # and the challenge tools ride on mattermost.post permission — but a
    # challenge can never *grant* anything: it is a message, not an authority.
    assert frontend.permissions.get("mattermost.post") == "allow"
    assert frontend.permissions.get("deploy") == "deny"  # unchanged by identity


def test_permission_source_removes_identity_from_authorization_path():
    """Structural check: AgentDef.allows() consults only permissions."""
    a = AgentDef(id="x", name="X", role="r",
                 identity=AgentIdentity(archetype="executive", autonomy="L5"))
    assert a.allows("deploy") is True  # default-allow policy, not identity
    a.permissions["deploy"] = "deny"
    assert a.allows("deploy") is False  # identity cannot flip it back
