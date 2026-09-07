"""Budget Manager.

Tracks spend per scope (global / project / agent / task) against monthly and
daily limits and answers the question the whole system routes on:

    estimate → check budget → approve | downgrade | reject

Every model call records a UsageRecord; the manager updates budget counters
and emits events when thresholds are crossed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from agentos.config import Settings
from agentos.db.store import EntityStore
from agentos.domain.models import (
    Budget,
    BudgetDecision,
    BudgetScope,
    UsageRecord,
)

DAY_FORMAT = "%Y-%m-%d"


class BudgetManager:
    def __init__(self, settings: Settings, store: EntityStore, emit=None,
                 downgrade_picker=None) -> None:
        self.settings = settings
        self.store = store
        self._collection = "budgets"
        self.emit = emit  # async callable(type, payload, **kw) or None
        self.downgrade_picker = downgrade_picker  # async (tier) -> model_id | None

    # -- access -------------------------------------------------------------
    async def get(self, scope: BudgetScope, scope_id: str = "global") -> Budget:
        budget = await self.store.get(self._collection, self._key(scope, scope_id), Budget)
        if budget is None:
            budget = self._default(scope, scope_id)
            await self.store.save(self._collection, budget)
        self._roll_day(budget)
        return budget

    async def save(self, budget: Budget) -> None:
        await self.store.save(self._collection, budget)

    def _key(self, scope: BudgetScope, scope_id: str) -> str:
        return f"{scope.value}:{scope_id}"

    def _default(self, scope: BudgetScope, scope_id: str) -> Budget:
        s = self.settings
        if scope == BudgetScope.GLOBAL:
            return Budget(scope=scope, scope_id=scope_id,
                          monthly_limit=s.global_budget_monthly,
                          daily_limit=s.global_budget_daily,
                          day_bucket=datetime.now(timezone.utc).strftime(DAY_FORMAT))
        if scope == BudgetScope.PROJECT:
            return Budget(scope=scope, scope_id=scope_id, monthly_limit=s.default_project_budget,
                          day_bucket=datetime.now(timezone.utc).strftime(DAY_FORMAT))
        return Budget(scope=scope, scope_id=scope_id,
                      day_bucket=datetime.now(timezone.utc).strftime(DAY_FORMAT))

    @staticmethod
    def _roll_day(budget: Budget) -> bool:
        today = datetime.now(timezone.utc).strftime(DAY_FORMAT)
        if budget.day_bucket != today:
            budget.spent_day = 0.0
            budget.day_bucket = today
            return True
        return False

    # -- decisions ----------------------------------------------------------
    async def check(self, scope: BudgetScope, scope_id: str,
                    estimated_cost: float, suggested_tier: str = "t2") -> BudgetDecision:
        """Should we spend `estimated_cost` under this scope right now?"""
        if estimated_cost <= 0:
            return BudgetDecision(allowed=True, action="approve", reason="zero cost")
        budget = await self.get(scope, scope_id)
        within_month = budget.monthly_limit is None or budget.spent_month + estimated_cost <= budget.monthly_limit
        within_day = budget.daily_limit is None or budget.spent_day + estimated_cost <= budget.daily_limit
        if within_month and within_day:
            return BudgetDecision(allowed=True, action="approve",
                                  reason=f"within limits (month {budget.spent_month:.2f}, day {budget.spent_day:.2f})")
        if self.settings.auto_downgrade_on_budget and self.downgrade_picker:
            tiers = {"t3": "t2", "t2": "t1", "t1": "t0"}
            target = tiers.get(suggested_tier)
            if target:
                model_id = await self.downgrade_picker(target)
                if model_id:
                    return BudgetDecision(
                        allowed=True, action="downgrade",
                        reason=f"budget constraint at {scope.value}:{scope_id} — downgrading",
                        suggested_model=model_id,
                    )
        return BudgetDecision(
            allowed=False, action="reject",
            reason=f"budget exhausted at {scope.value}:{scope_id} "
                   f"(month {budget.spent_month:.2f}/{budget.monthly_limit}, "
                   f"day {budget.spent_day:.2f}/{budget.daily_limit})",
        )

    # -- recording ----------------------------------------------------------
    async def record(self, usage: UsageRecord) -> None:
        scopes: list[tuple[BudgetScope, str]] = [(BudgetScope.GLOBAL, "global")]
        if usage.project_id:
            scopes.append((BudgetScope.PROJECT, usage.project_id))
        if usage.agent_id:
            scopes.append((BudgetScope.AGENT, usage.agent_id))
        if usage.task_id:
            scopes.append((BudgetScope.TASK, usage.task_id))
        for scope, scope_id in scopes:
            budget = await self.get(scope, scope_id)
            budget.spent_month += usage.estimated_cost
            budget.spent_day += usage.estimated_cost
            await self.save(budget)
            if budget.monthly_limit and budget.spent_month >= budget.monthly_limit * 0.9:
                if self.emit:
                    await self.emit("budget.warning", {
                        "scope": scope.value, "scope_id": scope_id,
                        "spent": budget.spent_month, "limit": budget.monthly_limit,
                    }, severity="warning")

    async def summary(self) -> list[dict]:
        budgets = await self.store.list(self._collection, Budget)
        budgets.sort(key=lambda b: (b.scope.value, b.scope_id))
        return [b.model_dump(mode="json") for b in budgets]

    async def project_cost(self, project_id: str) -> float:
        budget = await self.get(BudgetScope.PROJECT, project_id)
        return budget.spent_month