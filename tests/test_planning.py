"""Dynamic planning (autonomous workflow intelligence) tests.

Simple requests must NOT blindly run every stage; the full pipeline stays
available for major projects."""

from __future__ import annotations

import pytest

from agentos.planning import DynamicPlanner


@pytest.fixture
def planner() -> DynamicPlanner:
    return DynamicPlanner()


def test_simple_request_gets_minimal_stages(planner):
    plan = planner.plan_stages("write a one-line readme")
    assert plan[0] == "understanding"
    assert plan[-1] == "report"
    # a trivial request does not run research/security/deploy
    middle = set(plan[1:-1])
    assert middle <= {"requirements", "implement-frontend", "testing", "review"}


def test_frontend_request_selects_design_and_frontend(planner):
    plan = planner.plan_stages("fix the broken login button on the website")
    assert "implement-frontend" in plan
    assert "security" not in plan  # no security audit for a button fix


def test_major_project_expands_to_full_pipeline(planner):
    plan = planner.plan_stages("launch a full saas product")
    for stage in ("research", "community", "requirements", "design",
                  "implement-frontend", "implement-backend", "testing",
                  "security", "review", "deploy"):
        assert stage in plan, f"missing {stage} in {plan}"


def test_explicit_marker_overrides_keywords(planner):
    goal = ("PLANNED_STAGES: [research, report] "
            "research the demand for a niche product")
    plan = planner.plan_stages(goal)
    assert plan == ["understanding", "research", "report"]


def test_workflow_built_from_templates(planner):
    workflow = planner.build_workflow("research the market", stages=["understanding", "research", "report"])
    assert workflow.entry_stage == "understanding"
    ids = [s.stage_id for s in workflow.stages]
    assert ids == ["understanding", "research", "report"]
    # linear chain: each stage points at the next
    assert workflow.stages[0].next == "research"
    assert workflow.stages[1].next == "report"
    assert workflow.stages[2].next is None


def test_unknown_stage_rejected(planner):
    with pytest.raises(KeyError):
        planner.build_workflow("x", stages=["nonexistent"])


def test_plan_summary_lists_agents(planner):
    summary = planner.plan_summary("research the market for a saas launch")
    assert summary["stages"][0] == "understanding"
    assert summary["agents"]  # the agents that would run the stages
    assert summary["count"] == len(summary["stages"])


@pytest.mark.asyncio
async def test_execute_dynamic_runs_only_planned_stages(svc):
    """The engine executes the dynamically planned workflow — a small request
    runs a handful of stages, not the full pipeline."""
    run = await svc.engine.execute_dynamic(
        "write a one-line README", user_id="test-human")
    assert run["status"] == "completed", run
    assert run["planned_stages"][0] == "understanding"
    assert run["planned_stages"][-1] == "report"
    assert len(run["planned_stages"]) <= 6, run["planned_stages"]

    project = await svc.projects.require(run["project_id"])
    tasks = await svc.tasks.by_project(project.project_id)
    # one task per planned stage (each completed)
    assert len(tasks) == len(run["planned_stages"])
    for task in tasks:
        assert task.status.value == "completed", f"{task.title} → {task.status}"
    # artifacts written for each stage
    workspace = svc.workspace / project.project_id
    written = list(workspace.rglob("artifacts/*.md"))
    assert len(written) >= len(run["planned_stages"]) - 1


@pytest.mark.asyncio
async def test_execute_dynamic_full_pipeline_available(svc):
    """Major-project goals can still request the full 0→100-style pipeline."""
    run = await svc.engine.execute_dynamic(
        "launch a full saas product", user_id="test-human", expand_full=True)
    assert len(run["planned_stages"]) >= 10, run["planned_stages"]
    assert "deploy" in run["planned_stages"]
    # the full pipeline correctly halts at the deploy approval gate
    assert run["status"] == "awaiting_approval", run
    from agentos.domain.models import ApprovalStatus

    pending = await svc.approvals.pending()
    assert pending, "a deploy approval must be pending"
    final = await svc.engine.approve(pending[0].approval_id,
                                     ApprovalStatus.APPROVED.value,
                                     decided_by="test-human")
    assert final["status"] == "completed", final


@pytest.mark.asyncio
async def test_workflow_planned_event_published(svc):
    await svc.engine.execute_dynamic("research the market", user_id="test-human")
    events = await svc.events.recent(limit=100, event_type="workflow.planned")
    assert events
    assert events[0].payload["stages"]