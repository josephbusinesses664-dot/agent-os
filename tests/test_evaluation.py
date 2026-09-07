"""Evaluation subsystem tests: deterministic evaluator, LLM-judge fallback,
datasets, benchmark runs, leaderboard + trajectory analysis."""

from __future__ import annotations

import pytest

from agentos.agents.runtime import AgentRunResult
from agentos.domain.models import EvaluationRecord
from agentos.evaluation import (
    DeterministicEvaluator,
    RegressionDataset,
    leaderboard,
    load_dataset,
    trajectory_analysis,
)
from agentos.evaluation.datasets import DatasetItem


@pytest.mark.asyncio
async def test_deterministic_evaluator_passes_evidence(svc):
    task = await svc.tasks.create("prj1", "Implement feature", "build it")
    outcome = AgentRunResult(
        content=("Implemented the feature, wrote tests, and ran them — all "
                 "passed. Verified the artifact exists and the report was "
                 "delivered."),
        artifacts=["src/feature.py", "tests/test_feature.py"], model="echo")
    record = await DeterministicEvaluator().evaluate(task, outcome)
    assert record.passed
    assert record.score >= 3.0


@pytest.mark.asyncio
async def test_deterministic_evaluator_fails_claims(svc):
    task = await svc.tasks.create("prj1", "Implement feature", "build it")
    outcome = AgentRunResult(
        content="This should work probably, I think it would need more time.",
        error=None, artifacts=[], model="echo")
    record = await DeterministicEvaluator().evaluate(task, outcome)
    assert not record.passed
    assert any("speculative" in r for r in record.reasons)


@pytest.mark.asyncio
async def test_judge_falls_back_offline(svc):
    """No judge model configured → deterministic fallback, never a crash."""
    task = await svc.tasks.create("prj1", "t", "d")
    outcome = AgentRunResult(content="done and verified", artifacts=["a.md"])
    judge = svc.evaluation.judge
    record = await judge.evaluate(task, outcome)
    assert record.evaluator in ("deterministic", "llm_judge")
    assert record.score >= 0.0


def test_dataset_load_and_items():
    ds = RegressionDataset(name="basic", items=[
        DatasetItem(title="t1", description="d", agent="test-engineer")])
    assert ds.items[0].agent == "test-engineer"
    assert load_dataset("does-not-exist") is None


@pytest.mark.asyncio
async def test_benchmark_run_end_to_end(svc):
    """Run the regression dataset through the real engine path."""
    summary = await svc.evaluation.run_dataset("basic")
    assert summary.total >= 4
    assert summary.avg_score > 0
    records = await svc.entity_store.list_docs("evaluation")
    assert len(records) >= summary.total
    # performance stats folded in
    stats = await svc.performance.stats("test-engineer", "all")
    assert stats.runs > 0
    assert stats.evaluations_total > 0


@pytest.mark.asyncio
async def test_leaderboard_report_from_records(svc):
    records = []
    for agent_id, passed, score in (("a1", True, 4.0), ("a1", True, 3.5),
                                    ("a2", False, 1.0)):
        records.append(EvaluationRecord(
            agent_id=agent_id, task_id="t", evaluator="deterministic",
            score=score, passed=passed))
    rows = leaderboard(records, group_by="agent_id")
    assert rows[0]["key"] == "a1"
    assert rows[0]["pass_rate"] == 1.0
    analysis = trajectory_analysis(records)
    assert analysis["total_failed"] == 1


@pytest.mark.asyncio
async def test_failure_categorization(svc):
    records = [
        EvaluationRecord(agent_id="a", task_id="t", evaluator="deterministic",
                         score=1.0, passed=False, fail_class="transient"),
        EvaluationRecord(agent_id="a", task_id="t2", evaluator="deterministic",
                         score=2.0, passed=False, fail_class="transient"),
    ]
    analysis = trajectory_analysis(records)
    assert analysis["fail_classes"]["transient"] == 2
    assert any("transient" in r for r in analysis["recommendations"])