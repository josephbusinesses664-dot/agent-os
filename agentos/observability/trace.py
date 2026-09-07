"""Tracer — structured telemetry for every meaningful action.

A trace is a tree of spans (agent → stage → model → tool → evaluator →
memory). Each span records tokens, cost, latency, error class and a result
summary, so a task can be replayed as a chain of concrete actions — the
observability backbone for Phoenix/DeepEval-style analysis. OTel-compatible
tracing can be layered behind this interface without touching callers.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import TraceSpan
from agentos.observability.events import EventBus


class Tracer:
    def __init__(self, store: EntityStore, events: Optional[EventBus] = None) -> None:
        self.store = store
        self.events = events
        self._collection = "traces"

    @asynccontextmanager
    async def span(self, *, kind: str, name: str, trace_id: str,
                   parent_span: Optional[str] = None, agent_id: Optional[str] = None,
                   task_id: Optional[str] = None, project_id: Optional[str] = None,
                   model: Optional[str] = None, tool: Optional[str] = None,
                   payload: Optional[dict] = None) -> AsyncIterator[TraceSpan]:
        span = TraceSpan(kind=kind, name=name, trace_id=trace_id,
                         parent_span=parent_span, agent_id=agent_id,
                         task_id=task_id, project_id=project_id,
                         model=model, tool=tool, payload=payload or {})
        start = time.perf_counter()
        await self.store.save(self._collection, span)
        try:
            yield span
        except Exception as exc:  # noqa: BLE001
            span.status = "error"
            span.error = str(exc)[:500]
            from agentos.agents.runtime import classify_error

            span.fail_class = classify_error(str(exc))
            raise
        finally:
            span.finished_at = datetime.now(timezone.utc)
            span.latency_ms = int((time.perf_counter() - start) * 1000)
            await self.store.save(self._collection, span)
            if self.events is not None:
                try:
                    await self.events.publish(
                        "trace.span", {
                            "span_id": span.span_id, "kind": span.kind,
                            "name": span.name, "status": span.status,
                            "latency_ms": span.latency_ms, "cost": span.cost,
                            "model": span.model, "tool": span.tool,
                            "error": span.error, "fail_class": span.fail_class,
                        },
                        project_id=project_id, task_id=task_id, agent_id=agent_id,
                        severity="error" if span.status == "error" else "info")
                except Exception:  # noqa: BLE001
                    pass

    async def record(self, span: TraceSpan) -> None:
        await self.store.save(self._collection, span)

    async def task_trace(self, task_id: str) -> list[dict]:
        """The full span chain for a task: agent → stage → model → tool → …"""
        spans = await self.store.list(self._collection, TraceSpan,
                                      predicate={"task_id": task_id})
        spans.sort(key=lambda s: s.started_at)
        return [s.to_dict() for s in spans]

    async def run_trace(self, run_id: str) -> list[dict]:
        spans = await self.store.list(self._collection, TraceSpan,
                                      predicate={"trace_id": run_id})
        spans.sort(key=lambda s: s.started_at)
        return [s.to_dict() for s in spans]

    async def recent(self, limit: int = 200) -> list[dict]:
        spans = await self.store.list(self._collection, TraceSpan)
        spans.sort(key=lambda s: s.started_at, reverse=True)
        return [s.to_dict() for s in spans[:limit]]

    async def summary(self) -> dict[str, Any]:
        spans = await self.store.list(self._collection, TraceSpan)
        total = len(spans)
        errors = sum(1 for s in spans if s.status == "error")
        cost = sum(s.cost for s in spans)
        by_kind: dict[str, int] = {}
        for s in spans:
            by_kind[s.kind] = by_kind.get(s.kind, 0) + 1
        return {"total_spans": total, "errors": errors, "cost": round(cost, 4),
                "by_kind": by_kind}