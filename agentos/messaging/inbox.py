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

    # -- collaboration helpers ----------------------------------------------
    async def send_task_request(self, sender: str, recipient: str, title: str,
                                description: str, *, project_id: str | None = None,
                                task_id: str | None = None,
                                priority: str = "normal") -> AgentMessage:
        return await self.send(MessageType.TASK_REQUEST, sender, recipient,
                               {"title": title, "description": description,
                                "task_id": task_id},
                               project_id=project_id, task_id=task_id,
                               priority=priority, requires_response=True)

    async def send_handoff(self, sender: str, recipient: str, *,
                           artifacts: list[str], note: str = "",
                           task_id: str | None = None,
                           project_id: str | None = None) -> AgentMessage:
        return await self.send(MessageType.HANDOFF, sender, recipient,
                               {"artifacts": artifacts, "note": note},
                               project_id=project_id, task_id=task_id,
                               priority="normal", requires_response=False)

    async def send_blocker(self, sender: str, recipient: str, reason: str, *,
                           task_id: str | None = None,
                           project_id: str | None = None) -> AgentMessage:
        return await self.send(MessageType.BLOCKER, sender, recipient,
                               {"reason": reason},
                               project_id=project_id, task_id=task_id,
                               priority="high", requires_response=True)

    async def send_challenge(self, sender: str, recipient: str, concern: str, *,
                             evidence: list[str] | None = None,
                             severity: str = "medium",  # low | medium | high | blocking
                             recommended_action: str = "",
                             claim: str = "",
                             scope: str = "",
                             task_id: str | None = None,
                             project_id: str | None = None) -> AgentMessage:
        """Structured disagreement (identity-driven).

        A challenge is a first-class organizational object: claim + evidence +
        severity + recommended action + scope. Not endless debate — the
        recipient (or their parent) resolves; the sender records.
        """
        payload = {
            "concern": concern,
            "claim": claim or concern,
            "evidence": evidence or [],
            "severity": severity,
            "recommended_action": recommended_action,
            "scope": scope,
            "status": "open",
        }
        return await self.send(MessageType.CHALLENGE, sender, recipient,
                               payload,
                               project_id=project_id, task_id=task_id,
                               priority="high" if severity in ("high", "blocking") else "normal",
                               requires_response=True)

    async def resolve_challenge(self, message_id: str, resolver: str, verdict: str,
                                *, rationale: str = "") -> AgentMessage:
        """Resolve a challenge: accept (change course), reject (continue with
        rationale), or escalate (pass upward). Records the decision as a
        DECISION message so the org moves on — bounded iterations."""
        original = await self.store.get(self._collection, message_id, AgentMessage)
        if original is None:
            raise KeyError(f"message {message_id} not found")
        if original.message_type != MessageType.CHALLENGE:
            raise ValueError(f"message {message_id} is not a challenge")
        if verdict not in ("accept", "reject", "escalate"):
            raise ValueError("verdict must be accept | reject | escalate")
        original.status = "answered"
        if isinstance(original.payload, dict):
            original.payload = {**original.payload,
                                "status": "resolved", "verdict": verdict,
                                "resolved_by": resolver, "rationale": rationale}
        await self.store.save(self._collection, original)
        return await self.send(
            MessageType.DECISION, resolver, original.sender,
            {"decision": f"challenge {verdict}", "verdict": verdict,
             "rationale": rationale,
             "challenge_id": message_id,
             "concern": (original.payload or {}).get("concern", "")},
            project_id=original.project_id, task_id=original.task_id,
            priority="high")

    async def unanswered(self, recipient: str, message_type: str | None = None,
                         limit: int = 20) -> list[AgentMessage]:
        messages = await self.inbox(recipient, unread_only=True, limit=limit)
        if message_type:
            messages = [m for m in messages if m.message_type.value == message_type]
        return messages