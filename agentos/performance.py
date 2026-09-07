"""Agent performance tracker (operational incentives).

Every completed run records correctness, verification status, quality
(review/eval scores), cost, latency, retries, tool efficiency and downstream
outcome. These statistics are consumed by the model router (weaker performers
get routed to stronger models) and delegation (better performers get more
suitable work). No cosmetic XP anywhere: the numbers drive real decisions.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import EvaluationRecord, PerformanceStats

DAY_FORMAT = "%Y-%m-%d"
WEEK_FORMAT = "%Y-W%U"


class PerformanceTracker:
    def __init__(self, store: EntityStore, emit=None) -> None:
        self.store = store
        self._collection = "performance"
        self.emit = emit

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------
    async def record_run(self, agent_id: str, *, outcome: Any, task: Any,
                         latency_ms: int = 0) -> PerformanceStats:
        """Fold one task outcome into the agent's stats (all windows)."""
        completed = outcome.error is None
        failed_tool_calls = sum(
            1 for r in getattr(outcome, "tool_results", []) if not r.get("ok"))
        tool_calls = len(getattr(outcome, "tool_calls", [])) or 0
        retries = getattr(task, "retry_count", 0) or 0
        meta = {
            "completed": completed,
            "cost": getattr(outcome, "cost", 0.0) or 0.0,
            "tokens": sum((u.prompt_tokens or 0) + (u.completion_tokens or 0)
                           for u in getattr(outcome, "usage", [])),
            "latency_ms": latency_ms,
            "retries": retries,
            "tool_calls": tool_calls,
            "failed_tool_calls": min(failed_tool_calls, tool_calls) if tool_calls else 0,
        }
        stats = await self._update(agent_id, "all", meta)
        await self._update(agent_id, "weekly", meta)
        await self._update(agent_id, "daily", meta)
        if self.emit:
            try:
                await self.emit("agent.performance", {
                    "agent": agent_id, "task": task.task_id,
                    "completed": completed, "cost": meta["cost"],
                    "success_rate": stats.success_rate,
                }, agent_id=agent_id, task_id=task.task_id,
                    severity="warning" if not completed else "info")
            except Exception:  # noqa: BLE001
                pass
        return stats

    async def record_downstream(self, agent_id: str, success: bool) -> None:
        """Fold a delegated child's outcome into the delegating agent's stats
        (self-improvement signal: leaders whose teams deliver are rewarded)."""
        for window in ("all", "weekly", "daily"):
            stats = await self._load(agent_id, window)
            stats.downstream_total += 1
            if success:
                stats.downstream_success += 1
            if stats.downstream_total:
                stats.downstream_rate = round(
                    stats.downstream_success / stats.downstream_total, 4)
            stats.updated_at = datetime.now(timezone.utc)
            await self.store.save(self._collection, stats)

    async def record_evaluation(self, record: EvaluationRecord) -> None:
        """Fold evaluator/review scores into agent stats (quality signal)."""
        if not record.agent_id:
            return
        for window in ("all", "weekly", "daily"):
            stats = await self._load(record.agent_id, window)
            prev_total = stats.evaluations_total
            prev_passed = stats.evaluations_passed
            stats.evaluations_total += 1
            if record.passed:
                stats.evaluations_passed += 1
            # fold review score into avg_review_score
            prev_avg = stats.avg_review_score * prev_total
            stats.avg_review_score = (prev_avg + record.score) / stats.evaluations_total
            stats.updated_at = datetime.now(timezone.utc)
            await self.store.save(self._collection, stats)
        if record.agent_id and record.passed:
            pass  # event below
        if self.emit:
            try:
                await self.emit("agent.evaluated", {
                    "agent": record.agent_id, "score": record.score,
                    "passed": record.passed, "evaluator": record.evaluator,
                }, agent_id=record.agent_id, task_id=record.task_id,
                    severity="warning" if not record.passed else "info")
            except Exception:  # noqa: BLE001
                pass

    async def _update(self, agent_id: str, window: str, meta: dict) -> PerformanceStats:
        stats = await self._load(agent_id, window)
        runs = stats.runs
        stats.runs += 1
        if meta["completed"]:
            stats.completed += 1
        else:
            stats.failed += 1
        stats.success_rate = round(stats.completed / stats.runs, 4) if stats.runs else 1.0
        stats.total_cost += meta["cost"]
        stats.avg_cost = round(stats.total_cost / stats.runs, 6)
        stats.total_tokens += meta["tokens"]
        stats.avg_latency_ms = round(
            (stats.avg_latency_ms * runs + meta["latency_ms"]) / stats.runs, 1)
        stats.total_retries += meta["retries"]
        stats.tool_calls += meta["tool_calls"]
        stats.failed_tool_calls += meta["failed_tool_calls"]
        if stats.tool_calls:
            stats.tool_efficiency = round(
                1 - stats.failed_tool_calls / stats.tool_calls, 4)
        stats.updated_at = datetime.now(timezone.utc)
        await self.store.save(self._collection, stats)
        return stats

    async def _load(self, agent_id: str, window: str) -> PerformanceStats:
        key = f"{agent_id}:{window}"
        stats = await self.store.get(self._collection, key, PerformanceStats)
        if stats is None:
            bucket = datetime.now(timezone.utc).strftime(DAY_FORMAT if window == "daily" else WEEK_FORMAT)
            stats = PerformanceStats(agent_id=agent_id, window=window, day_bucket=bucket)
            await self.store.save(self._collection, stats)
        else:
            today = datetime.now(timezone.utc).strftime(
                DAY_FORMAT if window == "daily" else WEEK_FORMAT)
            if stats.day_bucket != today:
                stats = PerformanceStats(agent_id=agent_id, window=window,
                                         day_bucket=today)
                await self.store.save(self._collection, stats)
        return stats

    # ------------------------------------------------------------------
    # Consumption
    # ------------------------------------------------------------------
    async def stats(self, agent_id: str, window: str = "all") -> PerformanceStats:
        return await self._load(agent_id, window)

    async def leaderboard(self, limit: int = 10, metric: str = "success_rate",
                          min_runs: int = 1) -> list[dict]:
        """Rank agents by an operational metric. Metrics: success_rate,
        avg_cost (ascending), tool_efficiency, avg_review_score, throughput."""
        entries = await self.store.list(self._collection, PerformanceStats)
        rows = [e for e in entries if e.window == "all" and e.runs >= min_runs]
        reverse = metric != "avg_cost"
        rows.sort(key=lambda e: getattr(e, metric, 0), reverse=reverse)
        return [{"agent_id": e.agent_id, "runs": e.runs, metric: getattr(e, metric),
                 "success_rate": e.success_rate, "avg_cost": e.avg_cost,
                 "avg_latency_ms": e.avg_latency_ms,
                 "tool_efficiency": e.tool_efficiency,
                 "avg_review_score": e.avg_review_score,
                 "evaluations_passed": e.evaluations_passed}
                for e in rows[:limit]]

    async def influence(self, agent_id: str) -> dict[str, Any]:
        """What routing should do for this agent, based on track record."""
        stats = await self._load(agent_id, "all")
        suggestion = {"tier_bump": 0, "reason": ""}
        if stats.runs < 3:
            return suggestion  # not enough evidence yet
        if stats.success_rate < 0.5:
            suggestion.update(tier_bump=1,
                              reason=f"success rate {stats.success_rate:.0%} "
                                     f"across {stats.runs} runs — routing to stronger model")
        elif stats.tool_efficiency < 0.7 and stats.tool_calls >= 5:
            suggestion.update(tier_bump=1,
                              reason=f"tool efficiency {stats.tool_efficiency:.0%} — "
                                     f"stronger reasoning model may plan better")
        elif stats.success_rate >= 0.9 and stats.runs >= 5:
            suggestion.update(tier_bump=-1,
                              reason=f"reliable ({stats.success_rate:.0%}) — eligible for cheaper model")
        return suggestion