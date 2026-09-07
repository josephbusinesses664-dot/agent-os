"""LLM-as-judge evaluator.

Routes a judge prompt to a strong model (tier from settings), parses an
explicit SCORE/VERDICT block, and falls back to the deterministic evaluator
when no judge model is configured or the response is unparseable — so
evaluation never silently vanishes offline.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from agentos.domain.models import ModelRequest

from .base import Evaluator, make_record
from .deterministic import DeterministicEvaluator

_SCORE_RE = re.compile(r"SCORE\s*:\s*(\d+(?:\.\d+)?)\s*/\s*5", re.IGNORECASE)
_VERDICT_RE = re.compile(r"VERDICT\s*:\s*(pass|fail|partial)", re.IGNORECASE)


class LLMJudgeEvaluator(Evaluator):
    name = "llm_judge"

    def __init__(self, router: Any, judge_tier: str = "t3",
                 fallback: Optional[Evaluator] = None) -> None:
        self.router = router
        self.judge_tier = judge_tier
        self.fallback = fallback or DeterministicEvaluator()

    async def evaluate(self, task: Any, outcome: Any,
                       *, context: Optional[dict] = None) -> Any:
        model_id = await self._pick_judge()
        if model_id is None:
            return await self.fallback.evaluate(task, outcome, context=context)
        prompt = self._build_prompt(task, outcome)
        try:
            request = ModelRequest(model_id=model_id, system=prompt,
                                   messages=[{"role": "user",
                                              "content": "Judge the run and output SCORE, VERDICT, REASONS."}],
                                   temperature=0.0, max_tokens=600)
            provider = await self._provider_for(model_id)
            if provider is None:
                return await self.fallback.evaluate(task, outcome, context=context)
            response = await provider.complete(request)
        except Exception:  # noqa: BLE001
            return await self.fallback.evaluate(task, outcome, context=context)

        text = response.content or ""
        score_m = _SCORE_RE.search(text)
        verdict_m = _VERDICT_RE.search(text)
        if not score_m:
            return await self.fallback.evaluate(task, outcome, context=context)
        score = float(score_m.group(1))
        verdict = (verdict_m.group(1) if verdict_m else
                   ("pass" if score >= 3.0 else "fail"))
        reasons = [line.strip("- ").strip() for line in text.splitlines()
                   if line.strip().lower().startswith(("reason", "-"))][:5] or [
            f"judge score {score:.1f}/5"]
        return make_record(task, outcome, evaluator=self.name, score=score,
                           passed=verdict != "fail" and score >= 3.0,
                           verdict=verdict, reasons=reasons,
                           model_id=model_id,
                           cost=response.estimated_cost,
                           latency_ms=0)

    async def _pick_judge(self) -> Optional[str]:
        try:
            for tier in (self.judge_tier, "t3", "t2"):
                model_id = await self.router.pick_for_provider(tier)
                if model_id:
                    return model_id
        except Exception:  # noqa: BLE001
            return None
        return None

    async def _provider_for(self, model_id: str):
        model_def = await self.router.registry.get(model_id)
        if model_def is None:
            return None
        return self.router.providers.get(model_def.provider)

    @staticmethod
    def _build_prompt(task: Any, outcome: Any) -> str:
        return (
            "You are a strict evaluator of agent task runs. Score the run "
            "0-5 on correctness, completeness and quality of evidence.\n\n"
            f"TASK: {getattr(task, 'title', '')}\n{getattr(task, 'description', '')}\n\n"
            f"MODEL USED: {getattr(outcome, 'model', 'unknown')}\n"
            f"ARTIFACTS: {', '.join(getattr(outcome, 'artifacts', []) or []) or 'none'}\n"
            f"ERROR: {getattr(outcome, 'error', None) or 'none'}\n\n"
            f"AGENT OUTPUT:\n{(getattr(outcome, 'content', '') or '')[:4000]}\n\n"
            "Respond with:\n"
            "SCORE: <n>/5\n"
            "VERDICT: pass|fail|partial\n"
            "REASONS:\n- <reason>\n- <reason>"
        )