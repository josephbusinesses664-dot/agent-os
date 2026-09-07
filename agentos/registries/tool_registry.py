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

    async def register(self, tool: ToolDef, handler: Optional[ToolHandler] = None) -> ToolDef:
        await self.store.save(self._collection, tool)
        if handler:
            self._handlers[tool.name] = handler
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