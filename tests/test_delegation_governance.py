"""Governance upgrade tests: purposeful delegation (Phase 4/5), role-aware
evaluation (Phase 6/7), risk-aware routing (Phase 8), security escalation
scenarios (Phase 24) and failure injection (Phase 27)."""

from __future__ import annotations

import pytest

from agentos.domain.models import AgentDef, AgentIdentity, Task
from agentos.models.router import complexity_score
from agentos.orchestration.delegation import DelegationEngine


# ---------------------------------------------------------------------------
# Phase 4/5: purposeful delegation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delegation_selects_expert_over_generic(svc):
    """A frontend task delegated by the CTO should pick frontend-lead over
    equally-hierarchical peers — expertise beats alphabetical order."""
    engine = DelegationEngine(svc.agent_registry,
                              performance=svc.performance,
                              instances=svc.agent_registry)
    decision = await engine.select("cto", "implement the frontend checkout page with responsive design")
    assert decision.selected == "frontend-lead"
    winner = next(c for c in decision.candidates if c.agent_id == decision.selected)
    assert any("skills match" in r or "affinity" in r for r in winner.reasons)


@pytest.mark.asyncio
async def test_delegation_decision_is_explainable(svc):
    engine = DelegationEngine(svc.agent_registry)
    decision = await engine.select("cto", "design the database schema for orders")
    text = decision.explanation()
    assert "delegation for" in text
    assert decision.selected in text
    # every candidate appears with a score
    for c in decision.candidates:
        assert c.agent_id in text


@pytest.mark.asyncio
async def test_delegation_stays_hierarchy_bounded(svc):
    """A worker without agent.delegate sees only its own (empty) pool —
    purposeful selection never widens authority."""
    engine = DelegationEngine(svc.agent_registry)
    decision = await engine.select("frontend-lead", "research the market for widgets")
    assert decision.selected is None
    assert "hierarchy" in decision.reason or "no eligible" in decision.reason


@pytest.mark.asyncio
async def test_delegation_permission_containment(svc):
    """A parent cannot launder a capability it lacks: requesting a deploy
    task without holding 'deploy' permission disqualifies every candidate."""
    engine = DelegationEngine(svc.agent_registry)
    # product-director does not hold deploy permission
    decision = await engine.select("product-director",
                                   "deploy the service to production now")
    assert decision.selected is None
    disqualified = [c for c in decision.candidates if not c.eligible]
    assert any("requester lacks 'deploy'" in d
               for c in disqualified for d in c.disqualifications)


@pytest.mark.asyncio
async def test_delegate_tool_auto_mode(svc):
    """agent='auto' runs purposeful selection through the executor path."""
    task = Task(task_id="t1", project_id="p1", title="x", description="")
    from agentos.domain.models import Project
    project = Project(project_id="p1", name="p", objective="o")
    from agentos.domain.models import AgentDef as _AD
    cto = await svc.agent_registry.get("cto")
    # executive-level delegation: the org chart grants agent.delegate to
    # the executive; emulate a delegated act from the CTO carrying that grant
    cto = _AD(**{**cto.model_dump(exclude={"identity"}),
                 "identity": cto.identity})
    cto.permissions["agent.delegate"] = "allow"
    ctx = svc.runtime(cto, task, project).ctx
    result = await svc.executor.execute(ctx, cto, "agent.delegate", {
        "agent": "auto",
        "description": "build the frontend login screen",
    })
    # the echo pipeline runs; selection must have picked the frontend expert
    assert result.get("ok") is True
    assert result.get("child") == "frontend-lead"
    assert "selection" in result  # explainable decision recorded


# ---------------------------------------------------------------------------
# Phase 6/7: role-aware evaluation
# ---------------------------------------------------------------------------

def _run(**kw):
    from agentos.agents.runtime import AgentRunResult
    r = AgentRunResult()
    for k, v in kw.items():
        setattr(r, k, v)
    return r


def test_qa_measured_on_verification_not_volume():
    from agentos.evaluation.role_aware import evaluate_run_role_aware
    qa = await_agent("qa-director")
    verified = evaluate_run_role_aware(qa, _run(content="done", verified=True))
    unverified = evaluate_run_role_aware(qa, _run(content="looks good, all done"))
    assert verified.score > unverified.score
    assert "verification before signoff" in " ".join(unverified.notes) or \
        unverified.score < verified.score


def await_agent(agent_id):
    """Build a minimal agent object with real identity for evaluation."""
    from agentos.agents.identities import AGENT_IDENTITIES
    return AgentDef(id=agent_id, name=agent_id, role="r",
                    identity=AGENT_IDENTITIES[agent_id])


def test_researcher_measured_on_uncertainty_honesty():
    from agentos.evaluation.role_aware import evaluate_run_role_aware
    res = await_agent("market-researcher")
    honest = evaluate_run_role_aware(res, _run(
        content="The evidence is insufficient; confidence is low; unknowns remain"))
    blind = evaluate_run_role_aware(res, _run(
        content="The market is definitely 5 billion dollars, guaranteed."))
    assert honest.score > blind.score


def test_executive_measured_on_decision_process():
    from agentos.evaluation.role_aware import ROLE_CRITERIA
    crit = ROLE_CRITERIA["executive"]
    assert "delegation_quality" in crit
    assert "resource_discipline" in crit
    assert "risk_awareness" in crit


@pytest.mark.asyncio
async def test_agent_level_role_evaluation_uses_real_stats(svc):
    from agentos.evaluation.role_aware import evaluate_agent_role_aware
    agent = await svc.agent_registry.get("security-reviewer")
    out = await evaluate_agent_role_aware(svc.performance, agent)
    assert out["archetype"] == "security"
    assert "verification" in str(out["criteria"])
    assert out["verdict"]  # explainable, not empty


# ---------------------------------------------------------------------------
# Phase 8: risk-aware routing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_risky_task_bumps_minimal_tolerance_agent(svc):
    """devops-engineer (minimal tolerance) on a production deploy gets a
    tier at least as strong as the same task with a high-tolerance agent,
    and the reason explains the risk-aware choice."""
    devops = AgentDef(id="devops-engineer", name="d", role="r",
                      model_policy={"tier": "t2", "max_tier": "t3"},
                      identity=AgentIdentity(archetype="operations",
                                             risk_tolerance="minimal"))
    growth = AgentDef(id="growth-agent", name="g", role="r",
                      model_policy={"tier": "t2", "max_tier": "t3"},
                      identity=AgentIdentity(archetype="marketing",
                                             risk_tolerance="high"))
    task = Task(task_id="t", project_id="p", title="x",
                description="deploy the payment service migration to production")
    model_a, reason_a = await svc.router.route(devops, task)
    model_b, reason_b = await svc.router.route(growth, task)

    async def tier_of(mid):
        m = await svc.model_registry.get(mid)
        return int(m.tier[1]) if m else -1

    ta, tb = await tier_of(model_a), await tier_of(model_b)
    assert ta >= tb, f"devops routed lower: {reason_a} vs {reason_b}"
    # explainability: risk note present when the risk path fired
    assert ("risk-aware" in reason_a) or ("risk-aware" in reason_b) or ta == tb


@pytest.mark.asyncio
async def test_risk_note_absent_without_risk_signals(svc):
    plain = Task(task_id="t", project_id="p", title="x",
                 description="write a haiku about spring")
    agent = await svc.agent_registry.get("content-agent")
    _, reason = await svc.router.route(agent, plain)
    assert "risk-aware" not in reason


def test_complexity_score_still_deterministic():
    assert complexity_score("implement a feature") >= 1
    assert complexity_score("") == 0
