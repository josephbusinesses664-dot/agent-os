"""Multi-agent collaboration tests: structured handoffs, escalation on
subagent failure, delegation limits, duplicate-work prevention, inbox-fed
context."""

from __future__ import annotations

import pytest

from agentos.domain.models import MessageType, Task


@pytest.mark.asyncio
async def test_structured_handoff_and_blocker(svc):
    msg = await svc.messages.send_handoff(
        "frontend-lead", "cto", artifacts=["a.tsx"], note="ready for review",
        task_id="t1", project_id="prj1")
    assert msg.message_type == MessageType.HANDOFF
    blocker = await svc.messages.send_blocker(
        "test-engineer", "qa-director", reason="env broken", task_id="t1",
        project_id="prj1")
    assert blocker.message_type == MessageType.BLOCKER
    assert blocker.requires_response
    unread = await svc.messages.unanswered("cto", "handoff")
    assert any(m.message_id == msg.message_id for m in unread)


@pytest.mark.asyncio
async def test_run_sends_task_result_to_parent(svc):
    project = await svc.projects.create("collab-test", "t")
    parent = await svc.agent_registry.get("executive")
    child = await svc.agent_registry.get("chief-of-staff")
    task = await svc.tasks.create(project.project_id, "summarize", "write a summary",
                                  assigned_agent=child.id)
    outcome = await svc.engine.run_single_task(task.task_id)
    assert outcome.error is None
    messages = await svc.messages.recent(limit=20)
    results = [m for m in messages if m.message_type == MessageType.TASK_RESULT
               and m.sender == child.id and m.recipient == parent.id]
    assert results, "child should notify its parent with a TASK_RESULT"


@pytest.mark.asyncio
async def test_subagent_failure_escalates_to_parent(svc):
    """A failing child escalates to its parent (recovery path)."""
    project = await svc.projects.create("esc-test", "t")
    parent = await svc.agent_registry.get("executive")
    child = await svc.agent_registry.get("chief-of-staff")
    # inject enough provider failures to exhaust failover AND the
    # strategy-change retry, so the child truly fails with a transient class
    svc.providers["echo"].inject_failure(8)
    parent_task = await svc.tasks.create(project.project_id, "parent", "parent work",
                                         assigned_agent=parent.id)
    result = await svc.engine.spawn_subagent(parent_task, child.id,
                                             "this subtask will hit a provider outage",
                                             depth=1)
    assert result.error is not None
    escalations = [m for m in await svc.messages.recent(limit=30)
                   if m.message_type == MessageType.ESCALATION]
    assert escalations, "failed child must escalate to parent"
    assert escalations[0].recipient == parent.id


@pytest.mark.asyncio
async def test_delegation_depth_limit(svc):
    from agentos.orchestration.engine import SpawnLimitError

    project = await svc.projects.create("depth-test", "t")
    parent = await svc.agent_registry.get("executive")
    task = await svc.tasks.create(project.project_id, "t", "d", assigned_agent=parent.id)
    with pytest.raises(SpawnLimitError):
        await svc.engine.spawn_subagent(task, "chief-of-staff", "deep", depth=99)


@pytest.mark.asyncio
async def test_duplicate_active_task_detection(svc):
    """While a subtask is active, an identical delegation must be rejected."""
    from agentos.orchestration.engine import SpawnLimitError

    project = await svc.projects.create("dup-test", "t")
    parent = await svc.agent_registry.get("executive")
    task = await svc.tasks.create(project.project_id, "t", "d", assigned_agent=parent.id)
    hash_key = f"{task.task_id}:chief-of-staff:same work"
    svc.engine._active_task_hashes[hash_key] = "occupied"  # simulate concurrent run
    with pytest.raises(SpawnLimitError):
        await svc.engine.spawn_subagent(task, "chief-of-staff", "same work", depth=1)


@pytest.mark.asyncio
async def test_delegate_tool_permission_gate(svc):
    """Only the child's parent (or an explicitly permitted agent) can delegate."""
    project = await svc.projects.create("delegate-test", "t")
    # 'documentation-agent' is not a parent of 'frontend-lead'
    caller = await svc.agent_registry.get("documentation-agent")
    task = await svc.tasks.create(project.project_id, "t", "d", assigned_agent=caller.id)
    from agentos.domain.models import AgentDef

    agent = AgentDef(id="documentation-agent", name="Docs", role="docs",
                     permissions={})
    ctx = svc.runtime(agent, task, project).ctx
    result = await svc.executor.execute(ctx, agent, "agent.delegate",
                                        {"agent": "frontend-lead", "description": "build ui"})
    assert not result["ok"]
    # denied at the policy layer (default-deny) or by the handler's
    # parent-relationship check — either way it is blocked technically
    assert ("denied by permission policy" in result["error"]
            or "may not delegate" in result["error"]), result


@pytest.mark.asyncio
async def test_runtime_includes_inbox_context(svc):
    project = await svc.projects.create("inbox-test", "t")
    await svc.messages.send("handoff", "executive", "frontend-lead",
                            {"note": "use the design tokens from memory"},
                            project_id=project.project_id)
    agent = await svc.agent_registry.get("frontend-lead")
    task = await svc.tasks.create(project.project_id, "t", "d", assigned_agent=agent.id)
    system, user = await svc.runtime(agent, task, project)._build_prompt(task)
    assert "design tokens" in system or "use the design tokens" in system