"""Task, memory and messaging tests."""

import pytest

from agentos.domain.models import MemoryScope, MessageType, TaskStatus


@pytest.mark.asyncio
async def test_task_dependency_unblocking(svc):
    project = await svc.projects.create("P", "objective")
    a = await svc.tasks.create(project.project_id, "Research")
    b = await svc.tasks.create(project.project_id, "Build", dependencies=[a.task_id])
    c = await svc.tasks.create(project.project_id, "Test", dependencies=[b.task_id])

    runnable = await svc.tasks.runnable_tasks(project.project_id)
    assert [t.task_id for t in runnable] == [a.task_id]

    await svc.tasks.set_status(a.task_id, TaskStatus.COMPLETED)
    # b stays blocked until its dependency is truly done; runnable now includes b
    b2 = await svc.tasks.get(b.task_id)
    assert b2.status == TaskStatus.PENDING
    runnable = await svc.tasks.runnable_tasks(project.project_id)
    assert b.task_id in [t.task_id for t in runnable]

    await svc.tasks.set_status(b.task_id, TaskStatus.COMPLETED)
    c2 = await svc.tasks.get(c.task_id)
    assert c2.status == TaskStatus.PENDING
    runnable = await svc.tasks.runnable_tasks(project.project_id)
    assert [t.task_id for t in runnable] == [c.task_id]


@pytest.mark.asyncio
async def test_memory_scoping(svc):
    await svc.memory.save(MemoryScope.PROJECT, "prj1", "Decided: Python for backend", kind="decision", importance=5)
    await svc.memory.save(MemoryScope.AGENT, "cto", "Prefers async patterns", kind="preference", importance=3)

    project_hits = await svc.memory.recall(MemoryScope.PROJECT, "prj1", query="backend decision")
    assert any("Python" in e.content for e in project_hits)

    agent_hits = await svc.memory.recall(MemoryScope.AGENT, "cto")
    assert len(agent_hits) == 1

    # different scope must not leak
    other = await svc.memory.recall(MemoryScope.PROJECT, "prj2")
    assert other == []


@pytest.mark.asyncio
async def test_memory_importance_gate(svc):
    entry = await svc.memory.remember_if_important(MemoryScope.ORG, "org", "minor detail", importance=1)
    assert entry is None
    entry = await svc.memory.remember_if_important(MemoryScope.ORG, "org", "important decision", importance=4)
    assert entry is not None


@pytest.mark.asyncio
async def test_structured_messaging(svc):
    msg = await svc.messages.send(MessageType.TASK_REQUEST, "cto", "frontend-lead",
                                  payload={"task": "build nav"}, project_id="p1",
                                  requires_response=True)
    inbox = await svc.messages.inbox("frontend-lead")
    assert len(inbox) == 1 and inbox[0].message_id == msg.message_id

    reply = await svc.messages.respond(msg.message_id, "frontend-lead", {"done": True})
    assert reply.response_to == msg.message_id
    answered = await svc.messages.inbox("frontend-lead")
    assert answered == []
    thread = await svc.messages.thread(msg.message_id)
    assert len(thread) == 2


@pytest.mark.asyncio
async def test_decisions_persisted(svc):
    project = await svc.projects.create("P2", "obj")
    record = await svc.projects.record_decision(
        project.project_id, "Use Postgres over Mongo",
        alternatives=["MongoDB", "SQLite"], reasoning="Transactions + maturity",
        decided_by="cto")
    decisions = await svc.projects.decisions(project.project_id)
    assert len(decisions) == 1
    assert decisions[0].decision_id == record.decision_id
    project = await svc.projects.get(project.project_id)
    assert record.decision_id in project.decisions