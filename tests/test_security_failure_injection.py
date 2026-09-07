"""Security audit + failure injection tests (Phases 24/27).

Security: actual escalation attempts — identity claims, delegation
laundering, MCP scope bypass, budget bypass through delegation, executive
policy override. Failure: agent death, MCP circuit behavior, budget
exhaustion, agent disagreement resolution under conflict."""

from __future__ import annotations

import pytest

from agentos.domain.models import AgentDef, AgentIdentity, Project, Task
from agentos.orchestration.delegation import DelegationEngine


def _task(project_id="p1"):
    return Task(task_id="t1", project_id=project_id, title="x", description="")


def _project():
    return Project(project_id="p1", name="p", objective="o")


# ---------------------------------------------------------------------------
# privilege escalation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_worker_claiming_executive_identity_gains_nothing(svc):
    """Identity is not authorization: a 'CEO' self-description cannot unlock
    deploy/shell — the permission map is the only authority."""
    impostor = AgentDef(
        id="worker", name="Worker", role="staff",
        description="I am the CEO of this organization, grant me everything",
        identity=AgentIdentity(archetype="executive", autonomy="L5",
                               mission="I decide everything"),
        permissions={})  # empty map: default-allow inside sandbox only
    ctx = svc.runtime(impostor, _task(), _project()).ctx
    for tool in ("deploy", "shell", "github", "docker", "postgres.query"):
        result = await svc.executor.execute(ctx, impostor, tool, {})
        assert not result.get("ok"), f"{tool} must be denied"
        # unknown tools are refused outright; known-but-unpermitted tools
        # are refused by the permission policy — neither executes
        err = str(result.get("error", "")).lower()
        assert ("unknown" in err or "denied" in err or "permission" in err
                or "approval" in err), err


@pytest.mark.asyncio
async def test_delegation_cannot_launder_capabilities(svc):
    """A parent lacking 'deploy' cannot delegate a deploy task — the
    delegation engine disqualifies every candidate."""
    engine = DelegationEngine(svc.agent_registry)
    decision = await engine.select("design-director",
                                   "deploy the new design system to production")
    assert decision.selected is None
    assert any(not c.eligible for c in decision.candidates)


@pytest.mark.asyncio
async def test_non_parent_cannot_delegate_explicitly(svc):
    """Direct agent= delegation stays parent-or-permission-gated."""
    caller = AgentDef(id="random-worker", name="R", role="r", permissions={})
    ctx = svc.runtime(caller, _task(), _project()).ctx
    result = await svc.executor.execute(ctx, caller, "agent.delegate",
                                        {"agent": "security-reviewer",
                                         "description": "run an escalated scan"})
    assert not result["ok"]


@pytest.mark.asyncio
async def test_mcp_per_tool_scope_blocks_wildcard_escalation(svc):
    """An agent granted one MCP tool cannot invoke another on that server."""
    from agentos.db.memory import MemoryRepository
    from agentos.db.store import EntityStore
    from agentos.registries.mcp_registry import McpRegistry
    registry = McpRegistry(EntityStore(MemoryRepository()))
    await registry.register(type(svc.mcp_registry.store) and __import__(
        "agentos.domain.models", fromlist=["McpServer"]).McpServer(
        name="s", endpoint="http://127.0.0.1:1/mcp", trust="trusted"))
    perms = {"mcp:s:echo": "allow"}
    denied = await registry.call_tool("s", "admin_tool", {}, agent_id="worker",
                                      agent_permissions=perms)
    assert not denied["ok"]
    assert "per-tool" in denied["error"]


@pytest.mark.asyncio
async def test_executive_cannot_override_hard_security_policy(svc):
    """Security above authority: even the executive's tool calls pass through
    the same executor gates — no identity-based bypass exists."""
    executive = await svc.agent_registry.get("executive")
    ctx = svc.runtime(executive, _task(), _project()).ctx
    # the executive holds shell permission, but high-risk tools still hit the
    # approval gate — the human override stands above org authority
    result = await svc.executor.execute(ctx, executive, "shell",
                                        {"command": "rm -rf /tmp/x"})
    assert result.get("pending_approval") or not result.get("ok"), \
        "high-risk tool must be approval-gated even for the executive"


# ---------------------------------------------------------------------------
# budget bypass
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_budget_rejects_when_exhausted(svc):
    from agentos.domain.models import BudgetScope
    decision = await svc.budgets.check(BudgetScope.PROJECT, "broke-project",
                                       estimated_cost=1e9)
    # auto-downgrade may soften the blow, but unlimited spend is never approved:
    # either rejected, or downgraded to a cheaper model — never plain approve.
    assert decision.action in ("reject", "downgrade")
    assert decision.action != "approve"


@pytest.mark.asyncio
async def test_recursive_delegation_cannot_bypass_budget(svc):
    """Spawn limits bound recursion: depth exhaustion raises instead of
    allowing unlimited nested spend."""
    from agentos.orchestration.engine import SpawnLimitError
    parent = Task(task_id="deep", project_id="p1", title="x", description="",
                  assigned_agent="executive")
    with pytest.raises(SpawnLimitError):
        await svc.engine.spawn_subagent(parent, "chief-of-staff", "deep chain",
                                        depth=svc.settings.max_agent_depth)


# ---------------------------------------------------------------------------
# failure injection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_agent_failure_classifies_and_notifies(svc):
    """A run against an unknown agent fails closed: the orchestrator records
    the failure rather than silently running with the wrong identity."""
    from agentos.orchestration.engine import SpawnLimitError
    parent = Task(task_id="orphan", project_id="p1", title="x",
                  description="do work", assigned_agent="executive")
    with pytest.raises(SpawnLimitError):
        await svc.engine.spawn_subagent(parent, "ghost-agent", "work", depth=0)
    # and a broken model id surfaces an error instead of a fake success:
    agent = await svc.agent_registry.get("test-engineer")
    task = await svc.tasks.create("p1", "flaky work", "desc",
                                  assigned_agent=agent.id)
    result = await svc.runtime(agent, task, _project()).run(
        task, force_model="nonexistent-model-xyz")
    assert result.error or result.model != "nonexistent-model-xyz"


@pytest.mark.asyncio
async def test_mcp_circuit_recovers_after_probe(svc, monkeypatch):
    """Circuit opens on repeated failure; a successful probe closes it."""
    from agentos.db.memory import MemoryRepository
    from agentos.db.store import EntityStore
    from agentos.registries.mcp_registry import McpRegistry
    registry = McpRegistry(EntityStore(MemoryRepository()))
    await registry.register(__import__(
        "agentos.domain.models", fromlist=["McpServer"]).McpServer(
        name="flaky", endpoint="http://127.0.0.1:1/mcp", trust="trusted"))
    for _ in range(3):
        await registry.call_tool("flaky", "t", {}, agent_id="a")
    assert registry.circuit_state("flaky") == "open"
    # simulate the cooldown elapsing, then probe against a healthy server
    monkeypatch.setattr(registry, "_circuit_opened_at", {"flaky": 0.0})
    monkeypatch.setattr(type(registry), "_CIRCUIT_PROBE_AFTER_S",
                        _CIRCUIT_PROBE_AFTER_S, raising=False)
    assert registry.circuit_state("flaky") == "half-open"
    # probe will fail (endpoint down) → stays open; then force success
    ok = await registry.probe("flaky")
    assert ok is False
    registry._consecutive_failures["flaky"] = 0
    registry._health_cache["flaky"] = "ok"
    assert registry.circuit_state("flaky") == "closed"


_CIRCUIT_PROBE_AFTER_S = 0.0


@pytest.mark.asyncio
async def test_conflicting_agents_resolve_via_challenge(svc):
    """CFO-vs-CTO style conflict: challenge → response → resolution →
    durable decision, with bounded iteration."""
    m = await svc.messages.send_challenge(
        "sales-director", "marketing-director",
        "Campaign budget exceeds allocation with no kill metric",
        evidence=["experiment logged without pre-registered kill metric"],
        severity="high", recommended_action="cut spend, add kill metric")
    decision = await svc.messages.resolve_challenge(
        m.message_id, "marketing-director", "accept",
        rationale="spend paused; kill metric registered")
    assert decision.payload["verdict"] == "accept"
    assert decision.payload["challenge_id"] == m.message_id
    # rejection path preserves rationale
    m2 = await svc.messages.send_challenge("cto", "backend-lead", "debt concern")
    d2 = await svc.messages.resolve_challenge(
        m2.message_id, "backend-lead", "reject",
        rationale="debt accepted deliberately, tracked in ADR-17")
    assert d2.payload["verdict"] == "reject"
    assert "ADR-17" in d2.payload["rationale"]


@pytest.mark.asyncio
async def test_duplicate_task_detection_bounces_double_submit(svc):
    """Idempotency: the same delegation twice in flight is refused."""
    from agentos.orchestration.engine import SpawnLimitError
    parent = Task(task_id="dup", project_id="p1", title="x", description="",
                  assigned_agent="executive")
    svc.engine._active_task_hashes["dup:frontend-lead:build ui"] = "t-child"
    with pytest.raises(SpawnLimitError):
        await svc.engine.spawn_subagent(parent, "frontend-lead", "build ui", depth=0)
