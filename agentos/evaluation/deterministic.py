"""Deterministic checklist evaluator.

Scores a run against concrete evidence: did it error? did it produce
artifacts? is the output substantive? does it use evidence language or
speculative claims? Fully offline and reproducible — the regression
backbone that never hallucinates a verdict.
"""

from __future__ import annotations

from typing import Any, Optional

from .base import Evaluator, make_record

_EVIDENCE_MARKERS = ("passed", "verified", "wrote", "created", "implemented",
                     "built", "ran", "tested", "artifact", "report", "found",
                     "analyzed", "completed", "delivered")
_SPECULATIVE_MARKERS = ("should work", "i think", "probably", "would need",
                        "might work", "in theory", "i believe", "should be")


class DeterministicEvaluator(Evaluator):
    name = "deterministic"

    def __init__(self, require_artifact: bool = True, min_output_len: int = 120) -> None:
        self.require_artifact = require_artifact
        self.min_output_len = min_output_len

    async def evaluate(self, task: Any, outcome: Any,
                       *, context: Optional[dict] = None) -> Any:
        score = 5.0
        reasons: list[str] = []

        if getattr(outcome, "error", None):
            score -= 2.5
            reasons.append(f"run errored: {str(outcome.error)[:120]}")

        artifacts = list(getattr(outcome, "artifacts", []) or [])
        if self.require_artifact and not artifacts:
            score -= 1.0
            reasons.append("no artifacts produced")

        content = getattr(outcome, "content", "") or ""
        if len(content) < self.min_output_len:
            score -= 0.5
            reasons.append(f"thin output ({len(content)} chars)")

        low = content.lower()
        evidence = sum(1 for m in _EVIDENCE_MARKERS if m in low)
        speculative = sum(1 for m in _SPECULATIVE_MARKERS if m in low)
        if evidence >= 2:
            score += 0.5
            reasons.append(f"evidence language present ({evidence} markers)")
        elif evidence == 0 and not artifacts:
            score -= 0.5
            reasons.append("no evidence markers, no artifacts")
        if speculative:
            score -= min(1.5, 0.5 * speculative)
            reasons.append(f"speculative language ({speculative} markers)")

        score = max(0.0, min(5.0, score))
        passed = score >= 3.0
        verdict = "pass" if passed else "fail"
        return make_record(task, outcome, evaluator=self.name, score=score,
                           passed=passed, verdict=verdict, reasons=reasons)