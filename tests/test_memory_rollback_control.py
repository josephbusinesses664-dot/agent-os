"""Tests for the governance-finishing features: memory permission-scoping
(Phase 16), rollback/compensation ledger (Phase 14), and the human control
plane (Phase 30)."""

from __future__ import annotations

import pytest

from agentos.domain.models import AgentDef, AgentIdentity, MemoryScope, Project, Task
from agentos.memory.scoping import ScopedMemoryStore, can_read, can_write


def _agent(agent_id="worker-1", parent=None, children=None, autonomy="L2"):
    return AgentDef(id=agent_id, name=agent_id, role="r", parent_agent=parent,
                    allowed_children=children or [],
                    identity=AgentIdentity(archetype="engineer", autonomy=autonomy))


def _task(project_id="p1", assigned=None):
    return Task(task_id="task-1", project_id=project_id, title="t", description="",
                assigned_agent=assigned)


# ---------------------------------------------------------------------------
# Phase 16: memory permission-scoping
# ---------------------------------------------------------------------------

def test_agent_reads_own_agent_scope_but_not_siblings():
    a = _agent("worker-1")
    b = _agent("worker-2")
    assert can_read(a, "agent", "worker-1")
    assert not can_read(b, "agent", "worker-1")  # sibling: denied


def test_parent_may_read_child_agent_memory():
    parent = _agent("cto", children=["frontend-lead"])
    assert can_read(parent, "agent", "frontend-lead")


def test_task_scope_read_requires_task_participation():
    t = _task(assigned="worker-1")
    assigned = _agent("worker-1")
    outsider = _agent("worker-9")
    assert can_read(assigned, "task", "task-1", task=t)
    assert not can_read(outsider, "task", "task-1", task=t)


def test_task_participant_matrix():
    """Participants: assignee, assignee's parent (supervision), and agents
    whose parent is the assignee (collaborators). Everyone else denied —
    including executives merely holding the task object."""
    t = _task(assigned="worker-1")
    assignee = _agent("worker-1")
    supervisor = _agent("lead", children=["worker-1"])
    collaborator = _agent("worker-2", parent="worker-1")
    exec_holding_task = _agent("ceo", autonomy="L5")
    assert can_read(assignee, "task", "task-1", task=t)
    assert can_read(supervisor, "task", "task-1", task=t)
    assert can_read(collaborator, "task", "task-1", task=t)
    assert not can_read(exec_holding_task, "task", "task-1", task=t)
    # unassigned task: nobody participates
    unassigned = _task(assigned=None)
    assert not can_read(assignee, "task", "task-1", task=unassigned)
    # writes: assignee and its parent only; collaborator is read-only
    assert can_write(assignee, "task", "task-1", task=t)
    assert can_write(supervisor, "task", "task-1", task=t)
    assert not can_write(collaborator, "task", "task-1", task=t)


def test_project_scope_read_requires_same_project():
    a = _agent("worker-1")
    assert can_read(a, "project", "p1", project_id="p1")
    assert not can_read(a, "project", "p2", project_id="p1")


def test_org_memory_writable_only_by_executive_level():
    worker = _agent("worker-1", autonomy="L2")
    director = _agent("cto", autonomy="L4")
    executive = _agent("executive", autonomy="L5")
    assert not can_write(worker, "org", "org")
    assert can_write(director, "org", "org")
    assert can_write(executive, "org", "org")
    # but everyone may READ org memory
    assert can_read(worker, "org", "org")


def test_user_scope_never_reachable_by_agents():
    a = _agent("worker-1", autonomy="L5")  # even L5
    assert not can_read(a, "user", "user-prem")
    assert not can_write(a, "user", "user-prem")


@pytest.mark.asyncio
async def test_scoped_recall_denial_returns_empty_and_audits(svc):
    scoped = ScopedMemoryStore(svc.memory, audit=svc.audit)
    outsider = _agent("worker-9")
    entries = await scoped.scoped_recall(outsider, "agent", "someone-else",
                                         query="anything")
    assert entries == []  # existence not disclosed
    audits = await svc.audit.query(limit=20, action="memory.recall_denied")
    assert any(getattr(a, "action", "") == "memory.recall_denied" for a in audits)


@pytest.mark.asyncio
async def test_scoped_save_org_denied_for_worker(svc):
    scoped = ScopedMemoryStore(svc.memory, audit=svc.audit)
    worker = _agent("worker-1", autonomy="L2")
    entry = await scoped.scoped_save(worker, "org", "org", "org-wide fact")
    assert entry is None  # denied
    director = _agent("cto", autonomy="L4")
    ok = await scoped.scoped_save(director, "org", "org", "org-wide fact")
    assert ok is not None and ok.memory_id


@pytest.mark.asyncio
async def test_memory_recall_tool_enforces_scoping(svc):
    """The runtime memory.recall tool goes through scoping: a worker cannot
    pull another agent's private memories through the tool path."""
    from agentos.tools.builtin import _h_memory_recall
    project = Project(project_id="p1", name="p", objective="o")
    task = _task("p1")
    a = _agent("worker-1")
    ctx = svc.runtime(a, task, project).ctx
    result = await _h_memory_recall(ctx, {"scope": "agent", "owner_id": "someone-else"})
    assert result["ok"] is True
    assert result["entries"] == []  # denied -> empty, not an error


# ---------------------------------------------------------------------------
# Phase 14: rollback / compensation ledger
# ---------------------------------------------------------------------------

def test_rollback_records_reversibility_honestly():
    from agentos.security.rollback import RollbackLedger
    ledger = RollbackLedger()
    e = ledger.record(tool="mcp.call", args={"server": "s"}, agent_id="a",
                      task_id="t", project_id="p")
    assert e.reversibility == "irreversible"  # no compensation -> honest worst case
    assert e.compensation_name == ""


@pytest.mark.asyncio
async def test_rollback_executes_registered_compensation():
    from agentos.security.rollback import RollbackLedger
    ledger = RollbackLedger()
    done = {}

    async def undo(entry):
        done["entry"] = entry.entry_id
        return {"ok": True}

    ledger.register_compensation("undo_thing", undo)
    e = ledger.record(tool="api.call", args={"q": 1}, agent_id="a",
                      reversibility="reversible", compensation_name="undo_thing")
    r = await ledger.rollback(e.entry_id)
    assert r["ok"] is True and done["entry"] == e.entry_id
    assert e.status == "rolled_back"
    # idempotent: rolling back again is a no-op
    r2 = await ledger.rollback(e.entry_id)
    assert r2["ok"] and r2.get("already_done")


@pytest.mark.asyncio
async def test_rollback_task_stops_at_first_failure():
    from agentos.security.rollback import RollbackLedger
    ledger = RollbackLedger()
    calls = []

    async def bad(entry):
        calls.append(entry.entry_id)
        raise RuntimeError("boom")

    async def good(entry):
        calls.append(entry.entry_id)
        return {"ok": True}

    ledger.register_compensation("bad", bad)
    ledger.register_compensation("good", good)
    e1 = ledger.record(tool="x", args={}, task_id="t", reversibility="reversible",
                       compensation_name="good")
    e2 = ledger.record(tool="y", args={}, task_id="t", reversibility="reversible",
                       compensation_name="bad")
    r = await ledger.rollback_task("t")
    assert r["ok"] is False
    assert e2.status == "failed"
    assert e1.status == "active"  # ordered compensation stops after failure


@pytest.mark.asyncio
async def test_executor_records_mutative_actions_with_undo(svc):
    """A filesystem.write through the executor lands in the rollback ledger
    with a working compensation; the write is then actually undone."""
    project = await svc.projects.create("rb-test", "t")
    task = await svc.tasks.create(project.project_id, "write file", "",
                                  assigned_agent="product-manager")
    agent = await svc.agent_registry.get("product-manager")
    ctx = svc.runtime(agent, task, project).ctx
    result = await svc.executor.execute(ctx, agent, "filesystem.write",
                                        {"path": "rollback_target.txt",
                                         "content": "undo me"})
    assert result["ok"] is True
    entry_id = result.get("rollback_entry")
    assert entry_id
    entry = svc.rollback.get(entry_id)
    assert entry.reversibility == "reversible"
    target = ctx.workspace / "rollback_target.txt"
    assert target.exists()
    # human-initiated rollback removes the file
    r = await svc.rollback.rollback(entry_id, operator="human")
    assert r["ok"] is True
    assert not target.exists()


# ---------------------------------------------------------------------------
# Phase 30: control plane API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_control_pipeline_endpoint(svc):
    from agentos.api.main import create_app
    app = create_app(svc)
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        data = client.get("/api/control/pipeline").json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_rollback_endpoints(svc):
    from agentos.api.main import create_app
    app = create_app(svc)
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        stats = client.get("/api/rollback").json()
        assert "stats" in stats and "active" in stats
        # unknown entry -> 409/503 style error, not a crash
        r = client.post("/api/rollback/rb_nope/rollback")
        assert r.status_code in (404, 409, 503)
