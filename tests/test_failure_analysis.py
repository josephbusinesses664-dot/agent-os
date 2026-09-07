"""Self-improvement tests: failure analysis → recommendations → better
selection (which agent/model/capability for which task class)."""

from __future__ import annotations

import pytest

from agentos.domain.models import EvaluationRecord
from agentos.evaluation.failure_analysis import (
    best_match,
    classify_task,
    failure_summary,
    recommendations,
)


def _record(agent_id, passed, score, fail_class=None, cost=0.1,
            latency_ms=100, task_id="t"):
    return EvaluationRecord(task_id=task_id, agent_id=agent_id, passed=passed,
                            score=score, fail_class=fail_class, cost=cost,
                            latency_ms=latency_ms, evaluator="deterministic")


def test_failure_summary_groups_by_class_and_agent():
    records = [
        _record("frontend-lead", False, 0.4, fail_class="transient", task_id="t1"),
        _record("frontend-lead", False, 0.5, fail_class="transient", task_id="t2"),
        _record("backend-lead", True, 0.9, task_id="t3"),
    ]
    summary = failure_summary(records)
    assert summary["total_failed"] == 2
    assert summary["by_class"] == {"transient": 2}
    assert summary["by_agent"]["frontend-lead"] == {"transient": 2}


def test_recommendations_from_failure_classes():
    records = [
        _record("a", False, 0.3, fail_class="transient", task_id="t1"),
        _record("a", False, 0.3, fail_class="transient", task_id="t2"),
        _record("b", False, 0.3, fail_class="logic", task_id="t3"),
        _record("c", False, 0.3, fail_class="logic", task_id="t4"),
        _record("d", False, 0.3, fail_class="permission", task_id="t5"),
    ]
    recs = recommendations(records)
    assert any("retry budget" in r for r in recs)
    assert any("stronger model tier" in r for r in recs)
    assert any("permission" in r for r in recs)


def test_recommendations_clean_when_no_failures():
    records = [_record("a", True, 0.9, task_id="t1")]
    assert "no systematic failures" in recommendations(records)[0]


def test_classify_task_maps_to_capabilities():
    task_class, caps = classify_task("build a landing page with react")
    assert task_class == "landing"
    assert "frontend-engineering" in caps
    cls2, caps2 = classify_task("unknown vague thing")
    assert cls2 == "general" and caps2 == []


def test_best_match_uses_evaluation_history():
    records = [
        _record("frontend-lead", False, 0.4, fail_class="transient", task_id="t1"),
        _record("frontend-lead", False, 0.4, task_id="t2"),
        _record("backend-lead", True, 0.9, task_id="t3"),
        _record("backend-lead", True, 0.8, task_id="t4"),
    ]
    match = best_match(records, "build a landing page")
    # backend-lead has the better pass rate → recommended despite the topic
    assert match["recommended_agent"] == "backend-lead"
    assert match["task_class"] == "landing"
    assert "frontend-engineering" in match["recommended_capabilities"]
    assert match["note"] == "based on evaluation history"


def test_best_match_without_evidence_suggests_default_routing():
    match = best_match([], "research the market")
    assert match["recommended_agent"] is None
    assert "insufficient history" in match["note"]


def test_best_match_ranks_cost_and_latency():
    records = [
        _record("cheap-fast", True, 0.8, cost=0.01, latency_ms=20, task_id="t1"),
        _record("cheap-fast", True, 0.8, cost=0.01, latency_ms=20, task_id="t2"),
        _record("pricey-slow", True, 0.8, cost=0.5, latency_ms=900, task_id="t3"),
        _record("pricey-slow", True, 0.8, cost=0.5, latency_ms=900, task_id="t4"),
    ]
    match = best_match(records, "classify emails")
    # equal pass rate AND score → cheaper/faster wins (cost-conscious routing)
    assert match["recommended_agent"] == "cheap-fast"


@pytest.mark.asyncio
async def test_analyze_svc_reads_persisted_records(svc):
    from agentos.evaluation.failure_analysis import analyze_svc

    analysis = await analyze_svc(svc, goal="research the market")
    assert "failure_summary" in analysis
    assert "recommendations" in analysis
    assert "best_match" in analysis
    assert analysis["best_match"]["task_class"] == "research"