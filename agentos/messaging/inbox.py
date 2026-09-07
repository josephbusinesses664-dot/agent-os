"""Structured agent-to-agent messaging.

Agents communicate with structured messages (task_request, task_result,
question, approval, escalation, …) that are persisted — not just natural
language in a chat window. Each agent has an inbox it can drain.
"""

from __future__ import annotations

from typing import Any, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import AgentMessage, MessageType


class MessageBus:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "messages"

    async def send(self, message_type: MessageType | str, sender: str, recipient: str,
                   payload: dict[str, Any] | None = None, *, project_id: str | None = None,
                   task_id: str | None = None, priority: str = "normal",
                   requires_response: bool = False, response_to: str | None = None) -> AgentMessage:
        msg = AgentMessage(
            message_type=MessageType(message_type),
            sender=sender,
            recipient=recipient,
            project_id=project_id,
            task_id=task_id,
            priority=priority,
            payload=payload or {},
            requires_response=requires_response,
            response_to=response_to,
        )
        await self.store.save(self._collection, msg)
        return msg

    async def inbox(self, recipient: str, unread_only: bool = True, limit: int = 50) -> list[AgentMessage]:
        messages = await self.store.list(self._collection, AgentMessage,
                                         predicate={"recipient": recipient})
        if unread_only:
            messages = [m for m in messages if m.status == "sent"]
        messages.sort(key=lambda m: m.created_at)
        return messages[-limit:]

    async def mark_delivered(self, message_id: str) -> None:
        msg = await self.store.get(self._collection, message_id, AgentMessage)
        if msg:
            msg.status = "delivered"
            await self.store.save(self._collection, msg)

    async def respond(self, message_id: str, sender: str, payload: dict[str, Any]) -> AgentMessage:
        original = await self.store.get(self._collection, message_id, AgentMessage)
        if original is None:
            raise KeyError(f"message {message_id} not found")
        original.status = "answered"
        await self.store.save(self._collection, original)
        return await self.send(
            MessageType.TASK_RESULT if original.message_type == MessageType.TASK_REQUEST else MessageType.QUESTION,
            sender=sender, recipient=original.sender,
            payload=payload, project_id=original.project_id, task_id=original.task_id,
            response_to=original.message_id,
        )

    async def thread(self, message_id: str) -> list[AgentMessage]:
        root = await self.store.get(self._collection, message_id, AgentMessage)
        if root is None:
            return []
        all_msgs = await self.store.list(self._collection, AgentMessage)
        out = [root]
        frontier = [root.message_id]
        while frontier:
            current = frontier.pop(0)
            out.extend(m for m in all_msgs if m.response_to == current)
            frontier.extend(m.message_id for m in all_msgs if m.response_to == current)
        return out

    async def recent(self, limit: int = 100) -> list[AgentMessage]:
        messages = await self.store.list(self._collection, AgentMessage)
        messages.sort(key=lambda m: m.created_at, reverse=True)
        return messages[:limit]