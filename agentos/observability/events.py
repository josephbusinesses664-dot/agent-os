"""Event Bus.

Every meaningful action publishes an Event (agent.started, task.completed,
model.requested, approval.requested, …). Events are persisted (queryable audit
trail) and fanned out to in-process subscribers — e.g. the Mattermost sink
and the agent-status tracker. Subscribers must be fast; slow work happens
behind asyncio tasks.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

from agentos.db.store import EntityStore
from agentos.domain.models import Event

logger = logging.getLogger("agentos.events")

Subscriber = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "events"
        self._subscribers: list[Subscriber] = []

    def subscribe(self, fn: Subscriber) -> None:
        self._subscribers.append(fn)

    async def publish(self, event_type: str, payload: dict | None = None,
                      *, source: str = "system", project_id: str | None = None,
                      task_id: str | None = None, agent_id: str | None = None,
                      severity: str = "info") -> Event:
        event = Event(type=event_type, source=source, project_id=project_id,
                      task_id=task_id, agent_id=agent_id, severity=severity,
                      payload=payload or {})
        await self.store.save(self._collection, event)
        for fn in list(self._subscribers):
            try:
                asyncio.create_task(fn(event))
            except Exception:  # noqa: BLE001
                logger.exception("event subscriber failed")
        return event

    async def recent(self, limit: int = 100, event_type: str | None = None,
                     project_id: str | None = None) -> list[Event]:
        events = await self.store.list(self._collection, Event)
        if event_type:
            events = [e for e in events if e.type == event_type]
        if project_id:
            events = [e for e in events if e.project_id == project_id]
        events.sort(key=lambda e: e.ts, reverse=True)
        return events[:limit]

    async def count_by_type(self, limit: int = 200) -> dict[str, int]:
        events = await self.store.list(self._collection, Event)
        counts: dict[str, int] = {}
        for e in events[:limit]:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts