"""MCP Registry and client.

The registry tracks MCP servers (transport, endpoint, tools, permissions,
risk, required credentials). Only tools the requesting agent is authorized to
use are ever surfaced. The client speaks the MCP streamable-HTTP JSON-RPC
protocol so any standards-compliant MCP server can be connected.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx

from agentos.db.store import EntityStore
from agentos.domain.models import McpServer


class McpClient:
    """Minimal MCP streamable-HTTP client (JSON-RPC 2.0 over HTTP)."""

    def __init__(self, server: McpServer) -> None:
        self.server = server
        self._session_id: Optional[str] = None

    async def initialize(self) -> dict:
        return await self._request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "agent-os", "version": "0.1.0"},
        })

    async def list_tools(self) -> list[str]:
        result = await self._request("tools/list", {})
        return [t.get("name", "") for t in result.get("tools", [])]

    async def call_tool(self, tool: str, args: dict) -> dict:
        return await self._request("tools/call", {"name": tool, "arguments": args})

    async def _request(self, method: str, params: dict) -> dict:
        if not self.server.endpoint:
            raise ValueError(f"MCP server {self.server.name} has no endpoint")
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self.server.endpoint, headers=headers, json=body)
            resp.raise_for_status()
        if "mcp-session-id" in resp.headers:
            self._session_id = resp.headers["mcp-session-id"]
        text = resp.text
        # streamable-HTTP may return SSE frames; take the last data payload
        payload = text
        if "data:" in text:
            payload = text.strip().splitlines()[-1].removeprefix("data:").strip()
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = {"result": {"raw": text[:4000]}}
        if "error" in parsed:
            raise RuntimeError(parsed["error"])
        return parsed.get("result", parsed)


class McpRegistry:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "mcp"
        self._clients: dict[str, McpClient] = {}

    async def list(self, enabled_only: bool = True) -> list[McpServer]:
        servers = await self.store.list(self._collection, McpServer)
        servers.sort(key=lambda s: s.name)
        return [s for s in servers if s.enabled or not enabled_only]

    async def get(self, name: str) -> Optional[McpServer]:
        return await self.store.get(self._collection, name, McpServer)

    async def register(self, server: McpServer) -> McpServer:
        await self.store.save(self._collection, server)
        return server

    async def set_enabled(self, name: str, enabled: bool) -> McpServer:
        server = await self.get(name)
        if not server:
            raise KeyError(f"MCP server {name} not found")
        server.enabled = enabled
        await self.store.save(self._collection, server)
        return server

    def client_for(self, server: McpServer) -> McpClient:
        if server.name not in self._clients:
            self._clients[server.name] = McpClient(server)
        return self._clients[server.name]

    async def call_tool(self, server_name: str, tool: str, args: dict, agent_id: str = "") -> dict:
        server = await self.get(server_name)
        if not server:
            return {"ok": False, "error": f"unknown MCP server {server_name}"}
        if not server.enabled:
            return {"ok": False, "error": f"MCP server {server_name} disabled"}
        if server.permissions.get("default", "allow") == "deny" and agent_id not in server.permissions:
            return {"ok": False, "error": f"agent {agent_id} not authorized for {server_name}"}
        if server.tools and tool not in server.tools:
            return {"ok": False, "error": f"tool {tool} not exposed by {server_name}"}
        client = self.client_for(server)
        try:
            result = await client.call_tool(tool, args)
            return {"ok": True, "server": server_name, "tool": tool, "result": result}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}