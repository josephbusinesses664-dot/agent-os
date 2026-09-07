"""Security tests: permissions, approval gate, audit trail."""

import pytest

from agentos.domain.models import AgentDef, Task


@pytest.mark.asyncio
async def test_permission_denial_is_enforced(svc):
    """An agent without shell permission must have its shell call denied."""
    agent = AgentDef(id="safe-researcher", name="Safe", role="researcher",
                     permissions={"shell": "deny"})
    await svc.agent_registry.create(agent)
    task = Task(task_id="t-perm", project_id="p1", title="Check disk",
                description="PLANNED_TOOL_CALLS: [{\"tool\": \"shell\", \"args\": {\"command\": \"ls\"}}]")
    project = await svc.projects.create("P", "x")
    run = svc.runtime(agent, task, project)
    outcome = await run.run(task)
    assert outcome.error is None  # denial is a tool result, not a crash
    audit = await svc.audit.query(actor="safe-researcher", action="tool.denied")
    assert len(audit) >= 1
    assert audit[0].tool == "shell"


@pytest.mark.asyncio
async def test_high_risk_tool_requires_approval(svc):
    """Shell is high-risk: without an approval record it must not execute."""
    agent = AgentDef(id="dev-agent", name="Dev", role="dev",
                     permissions={"shell": "allow"})
    await svc.agent_registry.create(agent)
    task = Task(task_id="t-risky", project_id="p1", title="Deploy",
                description="PLANNED_TOOL_CALLS: [{\"tool\": \"shell\", \"args\": {\"command\": \"rm -rf /tmp/x\"}}]")
    project = await svc.projects.create("P", "x")
    run = svc.runtime(agent, task, project)
    outcome = await run.run(task)
    # the tool was gated: no execution, approval requested
    assert outcome.fail_class == "human_required"
    pending = await svc.approvals.pending()
    assert any(a.action == "tool:shell" for a in pending)
    audit = await svc.audit.query(actor="dev-agent", action="tool.approval_requested")
    assert len(audit) >= 1
    # and the shell command itself was never executed
    shell_calls = await svc.audit.query(actor="dev-agent", action="tool.called", tool="shell")
    assert shell_calls == []


@pytest.mark.asyncio
async def test_high_risk_tool_runs_after_approval(svc):
    agent = AgentDef(id="dev-agent-2", name="Dev2", role="dev",
                     permissions={"shell": "allow"})
    await svc.agent_registry.create(agent)
    project = await svc.projects.create("P", "x")
    task = Task(task_id="t-approved", project_id=project.project_id, title="Inspect",
                description="PLANNED_TOOL_CALLS: [{\"tool\": \"shell\", \"args\": {\"command\": \"ls\"}}]")
    # human grants approval: record it in task memory, then re-run with the marker
    await svc.memory.save("task", task.task_id, "approve:shell", kind="approval", importance=5)
    run = svc.runtime(agent, task, project)
    outcome = await run.run(task)
    assert outcome.error is None
    shell_calls = await svc.audit.query(actor="dev-agent-2", action="tool.called", tool="shell")
    assert len(shell_calls) >= 1


@pytest.mark.asyncio
async def test_audit_trail_records_actions(svc):
    project = await svc.projects.create("P", "x")
    await svc.audit.record("cto", "project.architected", project_id=project.project_id,
                           details={"scope": "core"})
    entries = await svc.audit.query(actor="cto", action="project.architected")
    assert len(entries) == 1
    assert entries[0].project_id == project.project_id
    assert entries[0].details["scope"] == "core"


@pytest.mark.asyncio
async def test_workspace_path_escape_blocked(svc):
    from agentos.tools.builtin import _path_inside

    workspace = svc.workspace
    with pytest.raises(PermissionError):
        _path_inside(workspace, "../../etc/passwd")
    ok = _path_inside(workspace, "artifacts/x.md")
    assert str(ok).startswith(str(workspace.resolve()))