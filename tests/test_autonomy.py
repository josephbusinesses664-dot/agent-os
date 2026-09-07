"""Autonomous integration test — the full agency loop, end to end.

USER GOAL → project → LangGraph workflow (plan → research → design →
implement → verify → review → report) → real tool execution → memory
updates → reviews → final artifacts → evaluation → performance stats.

This is the acceptance test for the upgraded system: if this passes, the
loop actually executes; nothing here is scaffolding or documentation.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_agency_loop_end_to_end(svc):
    run = await svc.engine.execute_goal(
        "Build a polished landing page for a boutique design agency.",
        user_id="test-human", workflow_id="agency_loop")
    assert run["status"] == "completed", run

    project = await svc.projects.require(run["project_id"])

    # 1. workflow stages all completed with artifacts
    tasks = await svc.tasks.by_project(project.project_id)
    assert len(tasks) >= 7, f"expected ~7 stage tasks, got {len(tasks)}"
    for task in tasks:
        assert task.status.value == "completed", f"{task.title} → {task.status}"

    # 2. real artifacts written to the project workspace
    workspace = svc.workspace / project.project_id
    artifacts = list(workspace.rglob("artifacts/*.md"))
    assert len(artifacts) >= 7, f"expected ≥7 artifact files, got {[str(a) for a in artifacts]}"
    report = workspace / "artifacts" / "final-report.md"
    assert report.exists()

    # 3. memory: project facts recorded with provenance (plan decision +
    #    report lesson, plus any facts extracted from stage outputs)
    mem = await svc.memory.by_owner("project", project.project_id)
    assert len(mem) >= 2, f"expected memory entries, got {len(mem)}"
    assert any(e.kind == "decision" for e in mem)
    assert any(e.kind == "lesson" for e in mem)
    assert all(e.provenance for e in mem)

    # 4. evaluation records for every stage
    records = await svc.entity_store.list_docs("evaluation")
    assert len(records) >= 7
    passed = sum(1 for r in records if r.get("passed"))
    assert passed >= 7, f"stages evaluated: {passed}/{len(records)} passed"

    # 5. performance stats recorded for the agents that worked
    stats = await svc.performance.stats("executive", "all")
    assert stats.runs >= 2  # plan + final report stages
    assert stats.evaluations_total >= 2

    # 6. telemetry: agent/stage/model/tool spans for a stage task
    first_task = tasks[0]
    spans = await svc.tracer.task_trace(first_task.task_id)
    kinds = {s["kind"] for s in spans}
    assert {"agent", "model", "tool"} <= kinds, kinds

    # 7. structured handoffs flowed up the org chart
    msgs = await svc.messages.recent(limit=100)
    assert any(m.message_type.value == "task_result" or m.message_type.value == "handoff"
               for m in msgs)

    # 8. audit log captured tool calls
    audit = await svc.audit.query(limit=200, tool="filesystem.write")
    assert audit, "filesystem.write calls must be audit-logged"


@pytest.mark.asyncio
async def test_verification_marks_artifacts(svc):
    """The verify step must not claim verified artifacts that are missing."""
    project = await svc.projects.create("verify-test", "t")
    agent = await svc.agent_registry.get("executive")
    task = await svc.tasks.create(project.project_id, "write missing file",
                                  "PLANNED_TOOL_CALLS: [{\"tool\":\"filesystem.write\","
                                  "\"args\":{\"path\":\"artifacts/real.md\",\"content\":\"AUTO\"}}]",
                                  assigned_agent=agent.id)
    runtime = svc.runtime(agent, task, project)
    # claim an artifact that was never written
    from agentos.agents.runtime import AgentRunResult

    result = AgentRunResult(content="done", artifacts=["artifacts/fake.md"])
    await runtime._verify_result(task, result)
    assert not result.verified
    assert "FAILED" in result.verification_note


@pytest.mark.asyncio
async def test_full_loop_recovers_from_transient_failure(svc):
    """A transient provider failure inside the loop must not sink the run:
    failover + strategy-change retry recover, and the workflow completes."""
    svc.providers["echo"].inject_failure(2)
    run = await svc.engine.execute_goal(
        "Write documentation for a CLI tool.",
        user_id="test-human", workflow_id="agency_loop")
    assert run["status"] == "completed", run
    project = await svc.projects.require(run["project_id"])
    workspace = svc.workspace / project.project_id
    assert (workspace / "artifacts" / "final-report.md").exists()
    # the recovery was observable: either model failover, a strategy-change
    # retry, or the graph-level stage retry absorbed the outage
    recovered = await svc.events.recent(limit=100, event_type="model.failover")
    recovered += await svc.events.recent(limit=100, event_type="agent.retry_strategy_changed")
    recovered += await svc.events.recent(limit=100, event_type="stage.retry")
    assert recovered, "recovery must be observable in the event stream"