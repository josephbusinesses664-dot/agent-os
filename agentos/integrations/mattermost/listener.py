"""Mattermost listener — polls channels for new human messages.

Polling (rather than WebSocket) keeps the integration simple and robust behind
proxies. New posts are fetched per channel since the last seen timestamp and
routed to the command handler.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

logger = logging.getLogger("agentos.mattermost.listener")


class MattermostListener:
    def __init__(self, service: Any, channel_names: list[str] | None = None) -> None:
        self.service = service
        self.channel_names = channel_names or ["town-square", "general", "executive",
                                               "approvals", "announcements"]
        self._since: dict[str, int] = {}
        self._running = False

    async def run(self, stop_event: Optional[asyncio.Event] = None) -> None:
        if not self.service.available:
            logger.info("mattermost listener idle (not connected)")
            while not (stop_event and stop_event.is_set()):
                await asyncio.sleep(10)
            return
        self._running = True
        interval = self.service.settings.mattermost_poll_interval
        logger.info("mattermost listener started (poll %ss)", interval)
        while not (stop_event and stop_event.is_set()):
            try:
                await self._poll_once()
            except Exception as exc:  # noqa: BLE001
                logger.warning("poll failed: %s", exc)
            await asyncio.sleep(interval)
        self._running = False
        logger.info("mattermost listener stopped")

    async def _poll_once(self) -> None:
        import time

        for logical in self.channel_names:
            channel_id = self.service.channels.get(logical)
            if not channel_id:
                continue
            since = self._since.get(logical, int(time.time()) - 60)
            posts = await self.service.client.posts_after(channel_id, since)
            for post in posts:
                if post.get("type", "") not in ("", "system_join_leave"):
                    continue
                if post.get("user_id") == self.service.bot_user_id:
                    continue
                await self.service.handle_message(post, self.service.svc.engine,
                                                  self.service.svc)
            self._since[logical] = int(time.time())