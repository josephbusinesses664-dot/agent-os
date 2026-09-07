"""Organizational benchmark harness tests (Phase 26, offline mode).

These verify the machinery of the full organizational chain — goal →
planner → delegation → authorization → skills → MCP → execution → audit —
deterministically, without a live model. The live adversarial run is gated
on real providers and MUST NOT be faked (tested below)."""

from __future__ import annotations

import pytest

from agentos.evaluation.benchmark import BENCHMARK_OBJECTIVE, OrgBenchmark


@pytest.mark.asyncio
async def test_offline_benchmark_full_chain_passes(svc):
    benchmark = OrgBenchmark(svc)
    report = await benchmark.run(mode="offline")
    assert report.mode == "offline"
    assert report.passed, report.summary()
    # every link of the chain was exercised
    names = [s.name for s in report.stages]
    for expected in ("goal_interpretation", "org_readiness", "delegation",
                     "authorization_gate", "skills", "mcp_governance",
                     "execution", "audit_trail"):
        assert expected in names, f"missing stage {expected}"
    assert "machinery, not model reasoning" in report.summary()


@pytest.mark.asyncio
async def test_offline_benchmark_authorization_gate_catches_laundering(svc):
    benchmark = OrgBenchmark(svc)
    report = await benchmark.run(mode="offline")
    stage = next(s for s in report.stages if s.name == "authorization_gate")
    assert stage.ok, "the harness must catch capability laundering"
    assert "refused" in stage.detail


@pytest.mark.asyncio
async def test_live_mode_refuses_without_real_provider(svc, monkeypatch):
    """No live keys → the live benchmark must refuse, not fall back to echo
    and pretend. This is the anti-faking guarantee."""
    monkeypatch.setattr(OrgBenchmark, "_live_available",
                        async_return_false)
    benchmark = OrgBenchmark(svc)
    with pytest.raises(RuntimeError, match="refusing to fake"):
        await benchmark.run(mode="live")


async def async_return_false(self):
    return False


@pytest.mark.asyncio
async def test_auto_mode_is_offline_with_echo_only(svc):
    """With only the echo provider configured, auto mode resolves offline —
    no silent pretending that echo results are model-backed autonomy."""
    benchmark = OrgBenchmark(svc)
    report = await benchmark.run(mode="auto")
    assert report.mode == "offline"


def test_objective_covers_full_org_scope():
    obj = BENCHMARK_OBJECTIVE.lower()
    for word in ("research", "design", "build", "test", "secure", "deploy"):
        assert word in obj
