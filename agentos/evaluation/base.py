"""Evaluation subsystem — shared types.

Evaluators answer "how good was this run?" with a score (0..5), a pass/fail
verdict and concrete reasons. Records are persisted and feed the performance
tracker, so evaluation directly shapes routing and delegation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from agentos.domain.models import EvaluationRecord, new_id


class Evaluator(ABC):
    name: str = "base"

    @abstractmethod
    async def evaluate(self, task: Any, outcome: Any, *, context: Optional[dict] = None) -> EvaluationRecord:
        """Score one task outcome."""


def make_record(task: Any, outcome: Any, *, evaluator: str, score: float,
                passed: bool, verdict: str, reasons: list[str],
                model_id: Optional[str] = None, agent_id: Optional[str] = None,
                skill_id: Optional[str] = None, workflow_id: Optional[str] = None,
                cost: float = 0.0, latency_ms: int = 0,
                fail_class: Optional[str] = None) -> EvaluationRecord:
    return EvaluationRecord(
        eval_id=new_id("evl"),
        task_id=getattr(task, "task_id", None),
        project_id=getattr(task, "project_id", None),
        agent_id=agent_id or getattr(task, "assigned_agent", None),
        model_id=model_id or getattr(outcome, "model", None),
        skill_id=skill_id,
        workflow_id=workflow_id or getattr(task, "workflow_id", None),
        evaluator=evaluator, score=max(0.0, min(5.0, score)), passed=passed,
        verdict=verdict, reasons=reasons, cost=cost or getattr(outcome, "cost", 0.0),
        latency_ms=latency_ms, fail_class=fail_class,
    )