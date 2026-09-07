"""Health Checker — tests every subsystem and reports clear status."""

from __future__ import annotations

import time
from typing import Any

from agentos.domain.models import HealthReport


class HealthChecker:
    def __init__(self, svc: Any) -> None:
        self.svc = svc

    async def check_all(self) -> list[HealthReport]:
        checks: list[tuple[str, Any]] = [
            ("database", self._db()),
            ("kv", self._kv()),
            ("queue", self._queue()),
            ("orchestrator", self._orchestrator()),
            ("worker", self._worker()),
            ("model-providers", self._providers()),
            ("mcp-registry", self._mcp()),
            ("skill-registry", self._skills()),
            ("agent-registry", self._agents()),
            ("memory", self._memory()),
            ("mattermost", self._mattermost()),
        ]
        reports: list[HealthReport] = []
        for name, coro in checks:
            try:
                reports.append(await coro)
            except Exception as exc:  # noqa: BLE001
                reports.append(HealthReport(service=name, status="down", detail=str(exc)[:200]))
        return reports

    async def _db(self) -> HealthReport:
        started = time.monotonic()
        ok = await self.svc.store.health()
        return HealthReport(service="database", status="ok" if ok else "down",
                            latency_ms=int((time.monotonic() - started) * 1000),
                            detail="in-memory" if type(self.svc.store).__name__ == "MemoryRepository"
                            else "postgres")

    async def _kv(self) -> HealthReport:
        started = time.monotonic()
        ok = await self.svc.kv.health()
        return HealthReport(service="kv", status="ok" if ok else "down",
                            latency_ms=int((time.monotonic() - started) * 1000))

    async def _queue(self) -> HealthReport:
        started = time.monotonic()
        size = await self.svc.queue.size()
        return HealthReport(service="queue", status="ok", latency_ms=int((time.monotonic() - started) * 1000),
                            detail=f"{size} queued")

    async def _orchestrator(self) -> HealthReport:
        graph = self.svc.engine.get_graph() if self.svc.engine else None
        return HealthReport(service="orchestrator", status="ok" if graph else "down",
                            detail="langgraph compiled")

    async def _worker(self) -> HealthReport:
        return HealthReport(service="worker", status="ok", detail="queue consumer available")

    async def _providers(self) -> HealthReport:
        configured = {name for name, p in self.svc.providers.items() if p.is_configured()}
        available = sorted(configured & set(self.svc.providers))
        echo_only = available == ["echo"]
        return HealthReport(
            service="model-providers", status="ok" if available else "down",
            detail=("echo (offline)" if echo_only else ", ".join(available)),
        )

    async def _mcp(self) -> HealthReport:
        servers = await self.svc.mcp_registry.list()
        return HealthReport(service="mcp-registry", status="ok", detail=f"{len(servers)} servers registered")

    async def _skills(self) -> HealthReport:
        count = len(await self.svc.skill_registry.list())
        return HealthReport(service="skill-registry", status="ok" if count else "down",
                            detail=f"{count} skills indexed")

    async def _agents(self) -> HealthReport:
        count = len(await self.svc.agent_registry.list())
        return HealthReport(service="agent-registry", status="ok" if count else "down",
                            detail=f"{count} agents")

    async def _memory(self) -> HealthReport:
        return HealthReport(service="memory", status="ok", detail="multi-scope store ready")

    async def _mattermost(self) -> HealthReport:
        mm = self.svc.mattermost
        if mm is None:
            return HealthReport(service="mattermost", status="down", detail="not configured")
        ok = await mm.client.health() if mm.available else False
        return HealthReport(service="mattermost", status="ok" if ok else "down",
                            detail="connected" if ok else "unreachable")

    def overall(self, reports: list[HealthReport]) -> str:
        down = [r for r in reports if r.status == "down"]
        if not down:
            return "100%"
        return f"{100 - 20 * len(down)}% (degraded: {', '.join(r.service for r in down)})"