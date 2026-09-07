"""Orchestration / LangGraph workflow tests."""

import pytest

from agentos.domain.models import ApprovalStatus


@pytest.mark.asyncio
async def test_workflow_runs_to_completion(svc):
    project = await svc.projects.create("Discovery", "Test objective", workflow_id="discovery")
    run = await svc.engine.run_workflow("discovery", project.project_id)
    assert run["status"] == "completed"
    stages = run["stage_results"]
    assert set(stages) == {"understanding", "discovery", "community_intelligence",
                           "opportunity", "decision"}
    for result in stages.values():
        assert result["status"] == "completed"
        assert result["model"] == "echo"
    project = await svc.projects.get(project.project_id)
    assert project.status.value == "completed"
    # artifacts written to the sandbox
    assert len(project.artifacts) >= 5


@pytest.mark.asyncio
async def test_approval_gate_pauses_and_resumes(svc):
    project = await svc.projects.create("Gated", "obj", workflow_id="build_feature")
    run = await svc.engine.run_workflow("build_feature", project.project_id)
    assert run["status"] == "awaiting_approval"
    assert run["stage_results"]["deploy"]["status"] == "completed"  # work done, gate pending

    pending = await svc.approvals.pending()
    assert len(pending) == 1
    approval_id = pending[0].approval_id

    # resume with approval
    run = await svc.engine.approve(approval_id, ApprovalStatus.APPROVED.value,
                                   decided_by="human")
    assert run["status"] == "completed"
    assert run["stage_results"]["deploy"]["status"] == "completed"
    project = await svc.projects.get(project.project_id)
    assert project.status.value == "completed"


@pytest.mark.asyncio
async def test_approval_rejection_fails_workflow(svc):
    project = await svc.projects.create("Rejected", "obj", workflow_id="build_feature")
    run = await svc.engine.run_workflow("build_feature", project.project_id)
    assert run["status"] == "awaiting_approval"
    pending = await svc.approvals.pending()
    run = await svc.engine.approve(pending[0].approval_id, ApprovalStatus.REJECTED.value,
                                   decided_by="human")
    assert run["status"] == "failed"
    assert "rejected" in run["error"].lower()


@pytest.mark.asyncio
async def test_transient_failure_retries_then_succeeds(svc):
    from agentos.models.mock import EchoProvider

    provider = svc.providers["echo"]
    assert isinstance(provider, EchoProvider)
    provider.inject_failure(2)  # first two requests fail

    project = await svc.projects.create("Retry", "obj", workflow_id="discovery")
    run = await svc.engine.run_workflow("discovery", project.project_id)
    assert run["status"] == "completed"
    understanding = run["stage_results"]["understanding"]
    assert understanding["status"] == "completed"
    # retries actually happened
    assert run["retry_count"] >= 1


@pytest.mark.asyncio
async def test_workflow_state_is_checkpointed(svc):
    """LangGraph checkpointer keeps per-run state; paused runs keep stage results."""
    project = await svc.projects.create("Checkpoint", "obj", workflow_id="build_feature")
    run = await svc.engine.run_workflow("build_feature", project.project_id)
    assert run["status"] == "awaiting_approval"
    assert run["stage_results"]["implementation"]["status"] == "completed"
    # a fresh look at the same run shows the same durable state
    saved = svc.engine._active_runs[run["run_id"]]["state"]
    assert saved["status"] == "awaiting_approval"
    assert "deploy" in saved["stage_results"]


@pytest.mark.asyncio
async def test_agent_spawn_depth_limit(svc):
    from agentos.orchestration.engine import SpawnLimitError

    project = await svc.projects.create("Spawn", "obj")
    parent = await svc.tasks.create(project.project_id, "parent", assigned_agent="cto")
    with pytest.raises(SpawnLimitError):
        await svc.engine.spawn_subagent(parent, "frontend-lead",
                                        "deep subtask", depth=svc.settings.max_agent_depth)


@pytest.mark.asyncio
async def test_agent_spawn_duplicate_detection(svc):
    from agentos.orchestration.engine import SpawnLimitError

    project = await svc.projects.create("Dup", "obj")
    parent = await svc.tasks.create(project.project_id, "parent", assigned_agent="cto")
    # run the spawn in a way that holds the hash: simulate by calling twice in sequence
    # (first one completes and releases the hash, so instead directly test the guard)
    engine = svc.engine
    hash_key = f"{parent.task_id}:frontend-lead:same work"
    engine._active_task_hashes[hash_key] = "existing-task"
    with pytest.raises(SpawnLimitError):
        await engine.spawn_subagent(parent, "frontend-lead", "same work", depth=0)
    engine._active_task_hashes.pop(hash_key, None)


@pytest.mark.asyncio
async def test_goal_creates_project_and_runs(svc):
    result = await svc.engine.execute_goal("Build a scheduling tool for agencies",
                                           user_id="test", workflow_id="discovery")
    assert result["status"] == "completed"
    project = await svc.projects.get(result["project_id"])
    assert project is not None
    assert "scheduling" in project.objective.lower()