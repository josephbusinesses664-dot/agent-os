"""MCP Registry, client and governance.

The registry tracks MCP servers (transport, endpoint, tools, permissions,
risk, required credentials) plus governance metadata: provenance, trust
level, allowed agents, per-tool trust, data sensitivity and rate limits.

Governance model (MCP upgrade):
- TRUST ladder: trusted > reviewed > untrusted > blocked. Trust influences
  discovery, recommendation and execution refusal — it never bypasses
  permissions. Untrusted servers require explicit per-call agent
  authorization and appear flagged in discovery output.
- PER-TOOL authorization: `mcp:<server>:<tool>` permission keys checked in
  the caller's permission set (an agent allowed one tool gains nothing else
  on the server). Wildcards are honored only as explicit config, never by
  default. The old per-server default-deny check still applies.
- HEALTH / CIRCUIT BREAKER: consecutive failures open the circuit
  (bounded retries: fail fast while open). A recovery probe (single live
  initialize) half-opens and closes the circuit on success. Health status:
  healthy → degraded → circuit_open. No infinite retry loops.
- SCHEMA CHANGE DETECTION: discovered tool lists are hashed; a changed hash
  invalidates the cache and emits `mcp.schema_changed` (removed/renamed
  tools are detected by set difference).
- TOOL SELECTION: `select_tools()` ranks candidate tools for a capability
  need, filtering by permission, trust, health, then ranking by relevance.
- INJECTION DEFENSE: `check_injection()` scans tool output for
  instruction-shaped content; findings mark results as untrusted data —
  results never become policy or permissions.
- OBSERVABILITY: every governed call emits an `mcp.call` event with agent,
  task, server, tool, latency, success, error category and the permission
  decision. Credentials are never included in events or logs.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any, Optional

import httpx

from agentos.db.store import EntityStore
from agentos.domain.models import McpServer

# trust ladder: higher = more trusted
TRUST_RANK = {"trusted": 3, "reviewed": 2, "untrusted": 1, "blocked": 0}

# circuit breaker thresholds
_CIRCUIT_OPEN_AFTER = 3        # consecutive failures → open
_CIRCUIT_PROBE_AFTER_S = 60.0  # seconds before a recovery probe is allowed


def _error_category(exc_or_text: Exception | str) -> str:
    text = str(exc_or_text).lower()
    if "timed out" in text or "timeout" in text:
        return "timeout"
    if any(k in text for k in ("connect", "connection", "unreachable", "refused")):
        return "unreachable"
    if "401" in text or "403" in text or "unauthorized" in text:
        return "auth"
    if "429" in text or "rate" in text:
        return "rate_limit"
    return "server"


class McpClient:
    """Minimal MCP streamable-HTTP client (JSON-RPC 2.0 over HTTP).

    Authentication is isolated per server: headers come from `server.auth`
    config or registry-supplied credentials (in-memory only, never logged).
    """

    def __init__(self, server: McpServer, credentials: Optional[dict] = None,
                 timeout: float = 30.0) -> None:
        self.server = server
        self._credentials = credentials or {}
        self._session_id: Optional[str] = None
        self._timeout = timeout

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

    def _auth_headers(self) -> dict:
        auth = self.server.auth or {}
        token = auth.get("token") or self._credentials.get("token")
        headers: dict = {}
        if not token:
            return headers
        auth_type = auth.get("type", "bearer")
        if auth_type == "bearer":
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "header":
            headers[auth.get("header", "Authorization")] = token
        elif auth_type == "basic":
            import base64

            raw = f"{auth.get('user', '')}:{token}".encode()
            headers["Authorization"] = "Basic " + base64.b64encode(raw).decode()
        return headers

    async def _request(self, method: str, params: dict) -> dict:
        if not self.server.endpoint:
            raise ValueError(f"MCP server {self.server.name} has no endpoint")
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        headers.update(self._auth_headers())
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
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


# ---------------------------------------------------------------------------
# Prompt-injection defense: tool output is DATA, never instructions.
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|system)\s+(instructions|prompts?)", re.I),
    re.compile(r"(reveal|send|exfil[^s]|leak|post|print)\s+(your\s+)?(api\s*key|secret|token|credential|password)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an|in)\s+\.?(dev|admin|root|god)\s*mode", re.I),
    re.compile(r"(call|invoke|execute|run)\s+(the\s+)?(shell|exec|deploy|admin)\s+tool", re.I),
    re.compile(r"new\s+(system\s+)?(instructions?|policy|rules?)\s*:", re.I),
    re.compile(r"grant\s+(yourself|me|us)\s+(permission|access)", re.I),
]


def check_injection(content: str) -> list[dict]:
    """Scan untrusted tool output for instruction-shaped content.

    Returns a list of findings (pattern + excerpt). Findings do NOT block
    the result; they mark it so the runtime and prompt present it as data
    and so audit can see attempted manipulation."""
    findings: list[dict] = []
    if not content:
        return findings
    for pattern in _INJECTION_PATTERNS:
        for m in pattern.finditer(content):
            findings.append({
                "pattern": pattern.pattern[:60],
                "excerpt": content[max(0, m.start() - 40):m.end() + 40][:120],
            })
            if len(findings) >= 5:
                return findings
    return findings


class McpRegistry:
    def __init__(self, store: EntityStore, *, event_bus: Any = None,
                 tracer: Any = None) -> None:
        self.store = store
        self._collection = "mcp"
        self._clients: dict[str, McpClient] = {}
        self._tool_cache: dict[str, list[dict]] = {}  # server -> discovered tools
        self._schema_hash: dict[str, str] = {}
        self._health_cache: dict[str, str] = {}
        self._credentials: dict[str, dict] = {}  # server -> token (in-memory only)
        # circuit breaker state per server
        self._consecutive_failures: dict[str, int] = {}
        self._circuit_opened_at: dict[str, float] = {}
        self._latency_ms: dict[str, list[int]] = {}
        self.event_bus = event_bus
        self.tracer = tracer

    # -- events --------------------------------------------------------------
    async def _emit(self, event: str, payload: dict, **kw) -> None:
        if self.event_bus is not None:
            try:
                await self.event_bus.publish(event, payload, **kw)
            except Exception:  # noqa: BLE001 — observability must never break calls
                pass

    def _record_latency(self, server: str, ms: int) -> None:
        lat = self._latency_ms.setdefault(server, [])
        lat.append(ms)
        if len(lat) > 50:
            del lat[:len(lat) - 50]

    def latency_summary(self, server: str) -> dict:
        lat = self._latency_ms.get(server) or []
        if not lat:
            return {"samples": 0}
        return {"samples": len(lat), "p50_ms": sorted(lat)[len(lat) // 2],
                "max_ms": max(lat)}

    # -- listing -------------------------------------------------------------
    async def list(self, enabled_only: bool = True) -> list[McpServer]:
        servers = await self.store.list(self._collection, McpServer)
        servers.sort(key=lambda s: s.name)
        return [s for s in servers if s.enabled or not enabled_only]

    async def list_public(self) -> list[dict]:
        """Serialized without credential material (for API/UI output)."""
        return [s.public_dict() for s in await self.list()]

    # -- credential isolation (in-memory only, never persisted/logged) ------
    async def set_credentials(self, server_name: str, token: str) -> None:
        self._credentials[server_name] = {"token": token}
        self._clients.pop(server_name, None)  # force reconnect with new auth

    async def get(self, name: str) -> Optional[McpServer]:
        return await self.store.get(self._collection, name, McpServer)

    async def register(self, server: McpServer) -> McpServer:
        await self.store.save(self._collection, server)
        self._clients.pop(server.name, None)
        self._tool_cache.pop(server.name, None)
        return server

    async def set_enabled(self, name: str, enabled: bool) -> McpServer:
        server = await self.get(name)
        if not server:
            raise KeyError(f"MCP server {name} not found")
        server.enabled = enabled
        await self.store.save(self._collection, server)
        if not enabled:
            self._clients.pop(name, None)
            self._tool_cache.pop(name, None)
        return server

    # -- trust ----------------------------------------------------------------
    @staticmethod
    def tool_trust(server: McpServer, tool: str) -> str:
        """Effective trust for one tool: per-tool override, else server trust."""
        override = server.tool_trust.get(tool)
        if override in TRUST_RANK:
            return override
        return server.trust if server.trust in TRUST_RANK else "untrusted"

    def _trust_gate(self, server: McpServer, tool: str, agent_id: str) -> Optional[str]:
        """Returns an error string when the trust gate refuses the call."""
        trust = self.tool_trust(server, tool)
        if trust == "blocked":
            return f"tool {tool} on {server.name} is BLOCKED by governance policy"
        if trust == "untrusted" and server.permissions.get("default", "allow") != "deny":
            # untrusted + not explicitly scoped: require the caller to be
            # explicitly authorized for this server (default-deny semantics).
            if agent_id and agent_id not in server.permissions:
                return (f"tool {tool} on untrusted server {server.name} requires "
                        f"explicit authorization for agent {agent_id}")
        return None

    # -- health / circuit breaker ---------------------------------------------
    def circuit_state(self, server_name: str) -> str:
        """closed (healthy) | open (failing) | half-open (probe due)."""
        if self._consecutive_failures.get(server_name, 0) >= _CIRCUIT_OPEN_AFTER:
            opened = self._circuit_opened_at.get(server_name, 0.0)
            if time.monotonic() - opened >= _CIRCUIT_PROBE_AFTER_S:
                return "half-open"
            return "open"
        if self._consecutive_failures.get(server_name, 0) > 0:
            return "degraded"
        return "closed"

    def health_status(self, server_name: str) -> str:
        circuit = self.circuit_state(server_name)
        if circuit == "open":
            return "circuit_open"
        if circuit == "half-open":
            return "recovering"
        cached = self._health_cache.get(server_name)
        if cached == "ok" and circuit == "degraded":
            return "degraded"
        return cached or "unknown"

    async def probe(self, server_name: str) -> bool:
        """Recovery probe: one live initialize. Returns True on success."""
        server = await self.get(server_name)
        if not server:
            return False
        try:
            await self.client_for(server).initialize()
        except Exception:  # noqa: BLE001
            self._circuit_opened_at[server_name] = time.monotonic()  # keep open
            return False
        self._consecutive_failures[server_name] = 0
        self._circuit_opened_at.pop(server_name, None)
        self._health_cache[server_name] = "ok"
        await self._emit("mcp.recovered", {"server": server_name})
        return True

    # -- connection lifecycle ----------------------------------------------
    async def connect(self, server_name: str) -> dict:
        """Initialize a session with the server (idempotent)."""
        server = await self.get(server_name)
        if not server:
            return {"ok": False, "error": f"unknown MCP server {server_name}"}
        client = self.client_for(server)
        try:
            result = await client.initialize()
            self._health_cache[server_name] = "ok"
            self._consecutive_failures[server_name] = 0
            self._circuit_opened_at.pop(server_name, None)
            return {"ok": True, "server": server_name, "capabilities": result}
        except Exception as exc:  # noqa: BLE001
            self._health_cache[server_name] = "error"
            self._consecutive_failures[server_name] = self._consecutive_failures.get(server_name, 0) + 1
            if self._consecutive_failures[server_name] >= _CIRCUIT_OPEN_AFTER:
                self._circuit_opened_at.setdefault(server_name, time.monotonic())
            return {"ok": False, "error": str(exc)}

    async def disconnect(self, server_name: str) -> None:
        self._clients.pop(server_name, None)
        self._tool_cache.pop(server_name, None)
        self._health_cache.pop(server_name, None)

    async def health_check(self, server_name: str) -> dict:
        """Probe a server: cached health/circuit state, else live initialize."""
        server = await self.get(server_name)
        if not server:
            return {"server": server_name, "status": "unknown", "detail": "not registered"}
        if not server.enabled:
            return {"server": server_name, "status": "down", "detail": "disabled"}
        if server.trust == "blocked":
            return {"server": server_name, "status": "blocked",
                    "detail": "blocked by governance policy"}
        status = self.health_status(server_name)
        if status == "circuit_open":
            return {"server": server_name, "status": "circuit_open",
                    "detail": f"{self._consecutive_failures.get(server_name, 0)} consecutive failures; "
                              f"recovery probe after {_CIRCUIT_PROBE_AFTER_S:.0f}s"}
        if status == "recovering":
            ok = await self.probe(server_name)
            return {"server": server_name, "status": "ok" if ok else "circuit_open",
                    "detail": "recovery probe " + ("succeeded" if ok else "failed")}
        if status in ("ok", "degraded"):
            return {"server": server_name, "status": status, "detail": "cached probe"}
        result = await self.connect(server_name)
        return {"server": server_name,
                "status": "ok" if result.get("ok") else "error",
                "detail": str(result.get("error", "connected"))[:200]}

    # -- tool discovery -----------------------------------------------------
    async def discover_tools(self, server_name: str, force: bool = False) -> list[dict]:
        """List a server's tools (cached; refresh with force=True).

        Schema-change detection: the discovered tool list is hashed; a changed
        hash invalidates the cache and emits `mcp.schema_changed`. Returns
        [] while the circuit is open (do not hammer a dead server)."""
        if not force and server_name in self._tool_cache:
            return self._tool_cache[server_name]
        server = await self.get(server_name)
        if not server:
            return []
        if self.circuit_state(server_name) == "open":
            return []
        client = self.client_for(server)
        try:
            names = await client.list_tools()
            self._consecutive_failures[server_name] = 0
        except Exception:  # noqa: BLE001
            self._consecutive_failures[server_name] = self._consecutive_failures.get(server_name, 0) + 1
            if self._consecutive_failures[server_name] >= _CIRCUIT_OPEN_AFTER:
                self._circuit_opened_at.setdefault(server_name, time.monotonic())
            tools = []
            self._tool_cache[server_name] = tools
            return tools
        tools = [{"name": n, "server": server_name,
                  "trust": self.tool_trust(server, n),
                  "permission_key": f"mcp:{server_name}:{n}"} for n in names]
        new_hash = hashlib.sha256(json.dumps(sorted(names)).encode()).hexdigest()[:16]
        old_hash = self._schema_hash.get(server_name)
        if old_hash is not None and old_hash != new_hash:
            old_names = {t["name"] for t in self._tool_cache.get(server_name, [])}
            removed = sorted(old_names - set(names))
            await self._emit("mcp.schema_changed",
                             {"server": server_name, "old_hash": old_hash,
                              "new_hash": new_hash, "removed_tools": removed})
        self._schema_hash[server_name] = new_hash
        self._tool_cache[server_name] = tools
        return tools

    def client_for(self, server: McpServer) -> McpClient:
        if server.name not in self._clients:
            self._clients[server.name] = McpClient(
                server, self._credentials.get(server.name))
        return self._clients[server.name]

    # -- authorization --------------------------------------------------------
    @staticmethod
    def agent_tool_permitted(agent_permissions: Optional[dict], server_name: str,
                             tool: str) -> bool:
        """Agent-side per-tool check against the caller's permission set.

        Precedence: explicit `mcp:<server>:<tool>` key → per-server
        `mcp:<server>` key → global `mcp.call`. Absent keys deny (an agent
        authorized for one MCP tool never gains every tool on the server)."""
        if agent_permissions is None:
            return True  # caller-side check not available (registry-level use)
        tool_key = f"mcp:{server_name}:{tool}"
        if tool_key in agent_permissions:
            return agent_permissions[tool_key] == "allow"
        server_key = f"mcp:{server_name}"
        if server_key in agent_permissions:
            return agent_permissions[server_key] == "allow"
        return agent_permissions.get("mcp.call", "deny") == "allow"

    def _authorized(self, server: McpServer, tool: str, agent_id: str,
                    agent_permissions: Optional[dict] = None) -> Optional[str]:
        """Full authorization check. Returns error string or None.

        Layers: governance (blocked/untrusted) → server-level permissions →
        allowed_agents → tool allowlist → agent-side per-tool permission
        (`mcp:<server>:<tool>`). Trust NEVER bypasses permission layers."""
        err = self._trust_gate(server, tool, agent_id)
        if err:
            return err
        if server.allowed_agents and agent_id and agent_id not in server.allowed_agents:
            return f"agent {agent_id} not in allowed_agents for {server.name}"
        if server.permissions.get("default", "allow") == "deny" and (
                not agent_id or agent_id not in server.permissions):
            return f"agent {agent_id} not authorized for {server.name}"
        if server.tools and tool not in server.tools:
            return f"tool {tool} not exposed by {server.name}"
        if not self.agent_tool_permitted(agent_permissions, server.name, tool):
            return (f"agent {agent_id} lacks permission {server.name}:{tool} "
                    f"(per-tool MCP scope)")
        return None

    # -- tool selection ---------------------------------------------------------
    async def select_tools(self, need: str, agent_id: str, *, limit: int = 5,
                           allow_untrusted: bool = False,
                           agent_permissions: Optional[dict] = None) -> list[dict]:
        """Rank candidate MCP tools for a capability need, for one agent.

        Pipeline: candidates → trust filter (blocked never; untrusted only
        when explicitly allowed) → server-side policy filter → agent-side
        per-tool permission filter → health filter (skip circuit-open
        servers) → keyword relevance ranking."""
        candidates: list[dict] = []
        for server in await self.list(enabled_only=True):
            if server.trust == "blocked":
                continue
            if self.circuit_state(server.name) == "open":
                continue
            discovered = await self.discover_tools(server.name)
            pool = discovered or [{"name": t} for t in server.tools]
            for tool in pool:
                name = tool.get("name", "")
                if not name:
                    continue
                trust = self.tool_trust(server, name)
                if trust == "blocked" or (trust == "untrusted" and not allow_untrusted
                                          and server.permissions.get("default", "allow") != "deny"):
                    continue
                if not self._agent_permitted(server, name, agent_id):
                    continue
                if not self.agent_tool_permitted(agent_permissions, server.name, name):
                    continue
                candidates.append({
                    "server": server.name, "tool": name, "trust": trust,
                    "permission_key": f"mcp:{server.name}:{name}",
                    "risk": server.risk_level,
                    "sensitivity": server.data_sensitivity,
                })
        scored: list[tuple[dict, int]] = []
        terms = [t for t in re.split(r"[^a-z0-9]+", need.lower()) if len(t) > 2]
        for c in candidates:
            hay = f"{c['server']} {c['tool']}".lower()
            score = sum(2 for t in terms if t in hay)
            score += TRUST_RANK.get(c["trust"], 1)
            scored.append((c, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [c for c, s in scored if s > 0][:limit]

    def _agent_permitted(self, server: McpServer, tool: str, agent_id: str) -> bool:
        """Permission-side check (caller's own permission set is enforced by
        the executor; this filters by the server's own policy)."""
        if server.allowed_agents and agent_id and agent_id not in server.allowed_agents:
            return False
        if server.tools and tool not in server.tools:
            return False
        if server.permissions.get("default", "allow") == "deny":
            return bool(agent_id) and agent_id in server.permissions
        return True

    # -- execution ----------------------------------------------------------------
    async def call_tool(self, server_name: str, tool: str, args: dict,
                        agent_id: str = "", task_id: str | None = None,
                        agent_permissions: Optional[dict] = None) -> dict:
        """Execute an MCP tool call through every governance gate, observed.

        Order: registration → enabled → blocked/untrusted trust gate →
        allowed_agents → server permissions → tool allowlist → agent-side
        per-tool permission → circuit breaker → client call → injection
        scan → health bookkeeping."""
        server = await self.get(server_name)
        started = time.perf_counter()

        async def _finish(ok: bool, error: str = "", decision: str = "allowed",
                          extra: dict | None = None) -> dict:
            latency = int((time.perf_counter() - started) * 1000)
            if ok:
                self._record_latency(server_name, latency)
            await self._emit("mcp.call", {
                "agent": agent_id, "task": task_id, "server": server_name,
                "tool": tool, "latency_ms": latency, "ok": ok,
                "error_category": _error_category(error) if error else "",
                "permission_decision": decision,
            }, task_id=task_id, agent_id=agent_id,
                severity="warning" if not ok else "info")
            result: dict = {"ok": ok}
            if error:
                result["error"] = error
            if extra:
                result.update(extra)
            return result

        if not server:
            return await _finish(False, f"unknown MCP server {server_name}", "unknown_server")
        if not server.enabled:
            return await _finish(False, f"MCP server {server_name} disabled", "disabled")
        err = self._authorized(server, tool, agent_id, agent_permissions)
        if err:
            return await _finish(False, err, "denied")
        if self.circuit_state(server_name) == "open":
            return await _finish(False,
                                 f"circuit open for {server_name} after "
                                 f"{self._consecutive_failures.get(server_name, 0)} failures",
                                 "circuit_open")
        client = self.client_for(server)
        try:
            result = await client.call_tool(tool, args)
        except Exception as exc:  # noqa: BLE001
            self._consecutive_failures[server_name] = self._consecutive_failures.get(server_name, 0) + 1
            if self._consecutive_failures[server_name] >= _CIRCUIT_OPEN_AFTER:
                self._circuit_opened_at.setdefault(server_name, time.monotonic())
            self._health_cache[server_name] = "error"
            return await _finish(False, str(exc), "denied",
                                 {"error_category": _error_category(exc)})
        self._consecutive_failures[server_name] = 0
        self._circuit_opened_at.pop(server_name, None)
        self._health_cache[server_name] = "ok"
        # injection scan: tool output is DATA, never instructions
        findings = check_injection(json.dumps(result)[:20000])
        # preserve the pre-upgrade success shape: {ok, server, tool, result}
        extra: dict = {"result": result}
        if findings:
            extra["injection_findings"] = findings
            extra["content_classification"] = "untrusted_data"
        return await _finish(True, extra=extra)
