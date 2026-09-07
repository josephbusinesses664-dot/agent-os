"""Tool Registry.

Holds tool definitions (permission key, risk level, category) and the handler
callables. Custom tools can be registered at runtime without touching core.
"""

from __future__ import annotations

from typing import Awaitable, Callable, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import ToolDef
from agentos.tools.builtin import HANDLERS, load_builtin_defs

ToolHandler = Callable[[object, dict], Awaitable[dict]]


class ToolRegistry:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "tools"
        self._handlers: dict[str, ToolHandler] = dict(HANDLERS)
        self._health_checks: dict[str, ToolHandler] = {}

    async def seed_defaults(self) -> int:
        existing = await self.list()
        if existing:
            return len(existing)
        for tool in load_builtin_defs().values():
            await self.store.save(self._collection, tool)
        return len(load_builtin_defs())

    async def list(self, enabled_only: bool = True) -> list[ToolDef]:
        tools = await self.store.list(self._collection, ToolDef)
        tools.sort(key=lambda t: t.name)
        return [t for t in tools if t.enabled or not enabled_only]

    async def get(self, name: str) -> Optional[ToolDef]:
        return await self.store.get(self._collection, name, ToolDef)

    async def register(self, tool: ToolDef, handler: Optional[ToolHandler] = None,
                       health_check: Optional[ToolHandler] = None) -> ToolDef:
        await self.store.save(self._collection, tool)
        if handler:
            self._handlers[tool.name] = handler
        if health_check:
            self._health_checks[tool.name] = health_check
        return tool

    def handler(self, name: str) -> Optional[ToolHandler]:
        return self._handlers.get(name)

    async def set_enabled(self, name: str, enabled: bool) -> ToolDef:
        tool = await self.get(name)
        if not tool:
            raise KeyError(f"tool {name} not found")
        tool.enabled = enabled
        await self.store.save(self._collection, tool)
        return tool

    # -- capability-based discovery -----------------------------------------
    async def discover(self, query: str = "", agent: Any = None,
                       limit: int = 10) -> list[ToolDef]:
        """Rank tools by relevance to a capability need (description + category
        + name tokens), filtered by the agent's permission policy. Keeps the
        tool list an agent sees proportional to the task, not the catalog."""
        import re as _re

        tools = await self.list(enabled_only=True)
        if agent is not None:
            tools = [t for t in tools if agent.allows(t.permission_key or t.name)]
        if not query:
            return tools[:limit]
        terms = {t for t in _re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2}
        scored: list[tuple[float, ToolDef]] = []
        for tool in tools:
            haystack = _re.findall(r"[a-z0-9]+",
                                   f"{tool.name} {tool.description} {tool.category}".lower())
            score = sum(1 for t in terms if t in haystack)
            if score:
                scored.append((score, tool))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [t for _, t in scored[:limit]] or tools[:limit]

    # -- health checks ------------------------------------------------------
    def register_health(self, name: str, check: ToolHandler) -> None:
        self._health_checks[name] = check

    async def health(self, name: str = "") -> dict:
        """Probe a tool (or all enabled tools): handler present, enabled,
        optional live check. Returns structured health reports."""
        if name:
            tool = await self.get(name)
            if not tool:
                return {"tool": name, "status": "unknown", "detail": "not registered"}
            return await self._health_one(tool)
        reports = []
        for tool in await self.list(enabled_only=True):
            reports.append(await self._health_one(tool))
        ok = sum(1 for r in reports if r["status"] == "ok")
        return {"status": "ok" if ok == len(reports) else "degraded",
                "healthy": ok, "total": len(reports), "tools": reports}

    async def _health_one(self, tool: ToolDef) -> dict:
        check = self._health_checks.get(tool.name)
        if tool.risk_level == "high" and not check:
            return {"tool": tool.name, "status": "ok", "detail": "high-risk (approval-gated), no live probe"}
        if check is None:
            return {"tool": tool.name, "status": "ok", "detail": "registered"}
        try:
            result = await check(None, {})
            return {"tool": tool.name,
                    "status": "ok" if result.get("ok") else "error",
                    "detail": str(result.get("error", "live probe passed"))[:200]}
        except Exception as exc:  # noqa: BLE001
            return {"tool": tool.name, "status": "error", "detail": str(exc)[:200]}

    async def categories(self) -> list[str]:
        tools = await self.list()
        return sorted({t.category for t in tools})