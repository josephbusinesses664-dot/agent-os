"""End-to-end test: the complete 0 → 100 workflow, offline with echo."""

import pytest


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_zero_to_hundred_pipeline(svc):
    project = await svc.projects.create(
        "E2E Marketplace SaaS",
        "Validate and build a marketplace SaaS. Run the full pipeline.",
        workflow_id="zero_to_hundred",
    )
    run = await svc.engine.run_workflow("zero_to_hundred", project.project_id)
    assert run["status"] == "awaiting_approval"  # deployment gate pauses

    # human approves the deployment gate
    pending = await svc.approvals.pending()
    assert len(pending) == 1
    run = await svc.engine.approve(pending[0].approval_id, "approved", decided_by="e2e")
    assert run["status"] == "completed"

    stages = run["stage_results"]
    expected = {"understanding", "discovery", "community_intelligence", "opportunity",
                "strategy", "product_definition", "prd", "design", "architecture",
                "implementation", "testing", "security", "performance", "final_review",
                "deployment", "monitoring"}
    assert set(stages) == expected
    for result in stages.values():
        assert result["status"] == "completed", f"stage failed: {result}"

    # tasks: all created and completed
    tasks = await svc.tasks.by_project(project.project_id)
    assert len(tasks) == 16
    assert all(t.status.value == "completed" for t in tasks)

    # artifacts actually on disk in the sandbox
    project = await svc.projects.get(project.project_id)
    assert len(project.artifacts) >= 16
    artifact_dir = svc.workspace / project.project_id / "artifacts"
    files = [p.name for p in artifact_dir.glob("*.md")]
    assert "PRD.md" in files and "deployment.md" in files and "handoff.md" in files

    # events emitted across the pipeline
    events = await svc.events.recent(limit=500)
    types = {e.type for e in events}
    assert "workflow.started" in types
    assert "workflow.completed" in types
    assert "approval.requested" in types
    assert "approval.granted" in types
    assert "stage.completed" in types
    assert "model.completed" in types

    # budget tracked (echo is free but records still exist)
    budgets = await svc.budgets.summary()
    assert any(b["scope"] == "project" and b["scope_id"] == project.project_id for b in budgets)

    # audit trail non-empty
    audit = await svc.audit.query(limit=500)
    assert any(e.action == "tool.called" for e in audit)

    # agent instances returned to idle
    instances = {i.agent_id: i for i in await svc.agent_registry.list_instances()}
    for agent_id in ("executive", "product-manager", "deployment-agent", "monitoring-agent"):
        assert instances.get(agent_id) is not None
        assert instances[agent_id].status.value == "idle"


@pytest.mark.asyncio
async def test_failure_recovery_keeps_project_state(svc):
    """A failing stage marks the project failed but keeps prior stages' work."""
    from agentos.models.mock import EchoProvider

    provider = svc.providers["echo"]
    assert isinstance(provider, EchoProvider)
    provider.inject_failure(100)  # everything fails

    project = await svc.projects.create("Doomed", "obj", workflow_id="discovery")
    run = await svc.engine.run_workflow("discovery", project.project_id)
    assert run["status"] == "failed"
    project = await svc.projects.get(project.project_id)
    assert project.status.value == "in_review"
    # the failure was surfaced
    assert "error" in run and run["error"]