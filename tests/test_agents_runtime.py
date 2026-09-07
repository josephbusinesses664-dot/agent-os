"""Agent runtime tests."""

import pytest

from agentos.domain.models import Task


@pytest.mark.asyncio
async def test_runtime_executes_tools_and_tracks_cost(svc):
    agent = await svc.agent_registry.get("product-manager")
    project = await svc.projects.create("P", "x")
    task = Task(task_id="t-runtime", project_id=project.project_id,
                title="Write a PRD",
                description="Produce the PRD and write it to artifacts/PRD.md. "
                            "PLANNED_TOOL_CALLS: [{\"tool\": \"filesystem.write\", "
                            "\"args\": {\"path\": \"artifacts/PRD.md\", \"content\": \"AUTO\"}}]")
    run = svc.runtime(agent, task, project)
    outcome = await run.run(task)
    assert outcome.error is None
    assert outcome.model == "echo"
    assert outcome.cost == 0.0  # echo is free
    assert outcome.content
    # artifact written inside the sandbox
    artifact_path = svc.workspace / project.project_id / "artifacts" / "PRD.md"
    assert artifact_path.exists()
    # usage was recorded
    assert len(outcome.usage) >= 1
    assert outcome.usage[0].model == "echo"


@pytest.mark.asyncio
async def test_runtime_never_repeats_tool_calls(svc):
    """The dedupe guard must prevent tool loops."""
    agent = await svc.agent_registry.get("test-engineer")
    project = await svc.projects.create("P", "x")
    task = Task(task_id="t-dedupe", project_id=project.project_id, title="Run checks",
                description="PLANNED_TOOL_CALLS: [{\"tool\": \"filesystem.write\", "
                            "\"args\": {\"path\": \"artifacts/check.md\", \"content\": \"AUTO\"}}]")
    run = svc.runtime(agent, task, project)
    outcome = await run.run(task)
    assert outcome.error is None
    writes = await svc.audit.query(actor="test-engineer", action="tool.called", tool="filesystem.write")
    assert len(writes) == 1  # executed exactly once despite the echo re-emitting it


@pytest.mark.asyncio
async def test_runtime_honesty_marker(svc):
    """Echo output is explicitly labeled as offline simulation."""
    agent = await svc.agent_registry.get("product-researcher")
    project = await svc.projects.create("P", "x")
    task = Task(task_id="t-honest", project_id=project.project_id, title="Research",
                description="Investigate the market.")
    run = svc.runtime(agent, task, project)
    outcome = await run.run(task)
    assert "offline" in outcome.content.lower()


@pytest.mark.asyncio
async def test_single_task_worker_path(svc):
    agent = await svc.agent_registry.get("documentation-agent")
    project = await svc.projects.create("P", "x")
    task = await svc.tasks.create(project.project_id, "Write README",
                                  assigned_agent=agent.id,
                                  description="Write README.md under artifacts/. "
                                              "PLANNED_TOOL_CALLS: [{\"tool\": \"filesystem.write\", "
                                              "\"args\": {\"path\": \"artifacts/README.md\", \"content\": \"AUTO\"}}]")
    outcome = await svc.engine.run_single_task(task.task_id)
    assert outcome.error is None
    task = await svc.tasks.get(task.task_id)
    assert task.status.value == "completed"
    assert task.artifacts


@pytest.mark.asyncio
async def test_worker_queue_loop_processes_tasks(svc):
    import asyncio

    agent = await svc.agent_registry.get("test-engineer")
    project = await svc.projects.create("P", "x")
    task = await svc.tasks.create(project.project_id, "Check", assigned_agent=agent.id,
                                  description="PLANNED_TOOL_CALLS: []")
    await svc.queue.enqueue({"task_id": task.task_id})
    stop = asyncio.Event()
    worker = asyncio.create_task(svc.engine.worker_loop(stop_event=stop))
    await asyncio.sleep(1.5)
    stop.set()
    await worker
    task = await svc.tasks.get(task.task_id)
    assert task.status.value == "completed"