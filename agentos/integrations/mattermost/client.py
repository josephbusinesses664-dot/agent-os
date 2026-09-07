"""Minimal Mattermost REST API client (personal access token auth)."""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger("agentos.mattermost")


class MattermostClient:
    def __init__(self, base_url: str, token: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url, timeout=timeout,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> dict:
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, payload: dict) -> dict:
        resp = await self._client.post(path, json=payload)
        resp.raise_for_status()
        return resp.json()

    # -- identity -----------------------------------------------------------
    async def me(self) -> dict:
        return await self._get("/api/v4/users/me")

    async def health(self) -> bool:
        try:
            resp = await self._client.get("/api/v4/system/ping")
            return resp.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    # -- teams / channels ---------------------------------------------------
    async def get_team_by_name(self, name: str) -> Optional[dict]:
        try:
            return await self._get(f"/api/v4/teams/name/{name}")
        except httpx.HTTPStatusError:
            return None

    async def create_team(self, name: str, display_name: str) -> dict:
        return await self._post("/api/v4/teams", {
            "name": name, "display_name": display_name, "type": "O",
        })

    async def get_channel_by_name(self, team_id: str, name: str) -> Optional[dict]:
        try:
            return await self._get(f"/api/v4/teams/{team_id}/channels/name/{name}")
        except httpx.HTTPStatusError:
            return None

    async def create_channel(self, team_id: str, name: str, display_name: str,
                             purpose: str = "") -> dict:
        return await self._post("/api/v4/channels", {
            "team_id": team_id, "name": name, "display_name": display_name,
            "type": "O", "purpose": purpose,
        })

    # -- posts --------------------------------------------------------------
    async def post(self, channel_id: str, message: str, root_id: Optional[str] = None) -> dict:
        payload: dict[str, Any] = {"channel_id": channel_id, "message": message}
        if root_id:
            payload["root_id"] = root_id
        return await self._post("/api/v4/posts", payload)

    async def posts_after(self, channel_id: str, since: int) -> list[dict]:
        resp = await self._get("/api/v4/channels/{}/posts".format(channel_id),
                               params={"since": since * 1000, "per_page": 200})
        order = resp.get("order", [])
        posts = resp.get("posts", {})
        return [posts[pid] for pid in order if pid in posts]

    async def get_post(self, post_id: str) -> dict:
        return await self._get(f"/api/v4/posts/{post_id}")

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        try:
            return await self._get(f"/api/v4/users/username/{username}")
        except Exception:  # noqa: BLE001
            return None

    # -- reactions ----------------------------------------------------------
    async def react(self, post_id: str, emoji: str) -> None:
        try:
            await self._post("/api/v4/reactions", {
                "user_id": (await self.me()).get("id", ""),
                "post_id": post_id, "emoji_name": emoji,
            })
        except Exception:  # noqa: BLE001
            logger.debug("reaction failed", exc_info=True)