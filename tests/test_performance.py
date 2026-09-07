"""Performance tracker tests: operational stats, leaderboard, router and
delegation influence."""

from __future__ import annotations

import pytest

from agentos.agents.runtime import AgentRunResult
from agentos.domain.models import AgentDef


@pytest.mark.asyncio
async def test_record_run_updates_stats(svc):
    task = await svc.tasks.create("prj1", "t", "d")
    outcome = AgentRunResult(content="done", artifacts=["a.md"], model="echo", cost=0.02,
                             usage=[])
    outcome.usage = []
    await svc.performance.record_run("executive", outcome=outcome, task=task, latency_ms=500)
    stats = await svc.performance.stats("executive", "all")
    assert stats.runs == 1
    assert stats.completed == 1
    assert stats.success_rate == 1.0
    assert stats.avg_cost == pytest.approx(0.02)
    assert stats.avg_latency_ms == pytest.approx(500)


@pytest.mark.asyncio
async def test_failed_run_counts_failures_and_tool_efficiency(svc):
    task = await svc.tasks.create("prj1", "t", "d")
    outcome = AgentRunResult(error="provider down", fail_class="transient",
                             tool_calls=[{"tool": "web.search"}, {"tool": "web.search"}],
                             tool_results=[{"ok": False}, {"ok": True}])
    await svc.performance.record_run("executive", outcome=outcome, task=task)
    stats = await svc.performance.stats("executive", "all")
    assert stats.runs == 1
    assert stats.failed == 1
    assert stats.success_rate == 0.0
    assert stats.tool_efficiency == pytest.approx(0.5)


@pytest.mark.asyncio
async def test_leaderboard_ranks_by_metric(svc):
    for agent_id in ("good-agent", "bad-agent"):
        for i in range(3):
            task = await svc.tasks.create("prj1", f"t-{agent_id}-{i}", "d")
            ok = agent_id == "good-agent"
            outcome = AgentRunResult(
                content="done work here" if ok else None,
                error=None if ok else "logic failure",
                fail_class=None if ok else "logic",
                artifacts=["x.md"] if ok else [])
            await svc.performance.record_run(agent_id, outcome=outcome, task=task)
    rows = await svc.performance.leaderboard(limit=5, metric="success_rate", min_runs=3)
    assert rows[0]["agent_id"] == "good-agent"
    assert rows[0]["success_rate"] == 1.0
    assert rows[-1]["agent_id"] == "bad-agent"


@pytest.mark.asyncio
async def test_router_influence_bumps_weak_performers(svc):
    agent = AgentDef(id="weak", name="Weak", role="tester",
                     model_policy={"tier": "t1", "max_tier": "t3"})
    for i in range(4):
        task = await svc.tasks.create("prj1", f"weak-{i}", "run some tests")
        outcome = AgentRunResult(error="logic failure", fail_class="logic")
        await svc.performance.record_run("weak", outcome=outcome, task=task)
    influence = await svc.performance.influence("weak")
    assert influence["tier_bump"] == 1
    assert "success rate" in influence["reason"]


@pytest.mark.asyncio
async def test_engine_pick_child_prefers_best_performer(svc):
    parent = await svc.agent_registry.get("cto")
    # seed performance so the pick is evidence-based
    for i in range(3):
        task = await svc.tasks.create("prj1", f"good-{i}", "d")
        await svc.performance.record_run(
            "backend-lead", outcome=AgentRunResult(content="ok", artifacts=["a"]),
            task=task)
    for i in range(3):
        task = await svc.tasks.create("prj1", f"bad-{i}", "d")
        await svc.performance.record_run(
            "frontend-lead",
            outcome=AgentRunResult(error="failed", fail_class="logic"),
            task=task)
    picked = await svc.engine.pick_child(parent, "build a service")
    assert picked == "backend-lead"