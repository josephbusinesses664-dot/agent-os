"""Tracing tests: spans are recorded with latency/cost/status, task traces
form the full agent→stage→model→tool chain."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_agent_run_produces_span_chain(svc):
    project = await svc.projects.create("trace-test", "t")
    agent = await svc.agent_registry.get("test-engineer")
    task = await svc.tasks.create(project.project_id, "run tests", "run the test suite",
                                  assigned_agent=agent.id)
    outcome = await svc.engine.run_single_task(task.task_id)
    assert outcome.error is None
    spans = await svc.tracer.task_trace(task.task_id)
    kinds = {s["kind"] for s in spans}
    assert "agent" in kinds
    assert "model" in kinds
    assert "tool" in kinds
    # agent span is the root: no parent
    agent_spans = [s for s in spans if s["kind"] == "agent"]
    assert agent_spans[0]["parent_span"] is None


@pytest.mark.asyncio
async def test_tool_span_records_error_status(svc):
    project = await svc.projects.create("trace-err", "t")
    agent = await svc.agent_registry.get("executive")
    task = await svc.tasks.create(project.project_id, "t", "d")
    ctx = svc.runtime(agent, task, project).ctx
    await svc.executor.execute(ctx, agent, "db.query",
                               {"db": "missing.db", "query": "SELECT 1"})
    spans = await svc.tracer.task_trace(task.task_id)
    tool_spans = [s for s in spans if s["kind"] == "tool" and s["tool"] == "db.query"]
    assert tool_spans
    assert tool_spans[0]["status"] == "error"


@pytest.mark.asyncio
async def test_trace_summary_counts(svc):
    project = await svc.projects.create("trace-sum", "t")
    agent = await svc.agent_registry.get("executive")
    task = await svc.tasks.create(project.project_id, "t", "d", assigned_agent=agent.id)
    await svc.engine.run_single_task(task.task_id)
    summary = await svc.tracer.summary()
    assert summary["total_spans"] >= 2
    assert summary["by_kind"]["agent"] >= 1