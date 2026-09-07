# MCP & Tools

## Tool model

Every tool has: name, description, permission key, risk level, category and a
handler. Built-ins: `filesystem.read/write` (sandbox-confined), `shell`
(high risk — approval-gated), `web.search`, `calculator`, `memory.recall/save`,
`project.state`, `mattermost.post`, `api.call`, `mcp.call`.

Tool execution is routed through the **ToolExecutor**, which enforces:

1. permission check against the agent's map (default deny for anything that
   can leave the sandbox),
2. approval gate for high-risk tools (`shell`, anything at
   `REQUIRE_APPROVAL_RISK`), creating an ApprovalRequest instead of executing,
3. audit logging of every call (args + result),
4. workspace confinement for file operations.

## MCP registry

```yaml
name: my-server
description: …
transport: streamable-http | stdio | builtin
endpoint: https://host/mcp
tools: [tool-a, tool-b]          # only these are exposed
permissions: {default: deny, my-agent: allow}
risk_level: medium
required_credentials: [MY_API_KEY]
enabled: true
# governance (unknown stays unknown — never invented):
trust: untrusted                 # trusted | reviewed | untrusted | blocked
owner: ""                        # provenance: who maintains this server
allowed_agents: []               # empty = all authorized agents
tool_trust: {tool-c: blocked}    # per-tool trust override
data_sensitivity: normal         # normal | sensitive | restricted
```

## MCP governance model

**Trust ladder.** `trusted` (official/internal/verified) > `reviewed`
(inspected) > `untrusted` (unknown provenance) > `blocked` (prohibited).
Trust influences discovery, recommendation and execution refusal — it never
bypasses permissions. Untrusted servers require the calling agent to be
explicitly listed in `permissions`, even when the server is default-allow.
Blocked servers refuse execution and report `blocked` health without a
network probe.

**Per-tool authorization.** The calling agent's permission set is checked
with precedence `mcp:<server>:<tool>` → `mcp:<server>` → `mcp.call`. An
agent allowed one tool on a server gains nothing else — no wildcard
escalation. Server-side gates (`permissions.default: deny`, `allowed_agents`,
`tools` allowlist) apply on top.

**Health & circuit breaker.** Consecutive failures open the circuit after 3
failures; while open, calls fail fast (no hammering a dead server) and
discovery returns empty. After a 60s cooldown a recovery probe (single live
`initialize`) half-opens the circuit; success closes it. Status ladder:
`healthy → degraded → circuit_open → (probe) → healthy`.

**Schema-change safety.** Discovered tool lists are hashed; a changed hash
invalidates the cache and emits `mcp.schema_changed` (with removed tools),
so stale assumptions are never silently reused.

**Tool selection.** `mcp.select` (or `McpRegistry.select_tools`) ranks
candidate tools for a capability need: trust filter → server policy →
agent per-tool permissions → health filter → keyword relevance. Agents are
progressively exposed only to tools they may actually use.

**Injection defense.** Tool output is DATA, never instructions.
`check_injection()` scans results for instruction-shaped content ("ignore
previous instructions", "send your API key to…", "you are now in admin
mode"…). Flagged results are not blocked — they are marked
`content_classification: untrusted_data` with `injection_findings`, so the
runtime, prompts and audit treat them as untrusted. Tool output can never
modify permissions or policy.

**Observability.** Every governed call emits an `mcp.call` event: agent,
task, server, tool, latency, success, error category, permission decision.
Credentials never appear in events, logs or serialized servers.

- Agents only ever see tools they are authorized to use.
- The client speaks the MCP streamable-HTTP JSON-RPC protocol; a `stdio`
  transport can be added by implementing the spawn path in `McpClient`.
- Every MCP call is audited; disabled servers stop surfacing immediately.
- Treat any MCP server with shell/deploy/file access as high risk until
  reviewed (source, license, dependencies, requested permissions).

```bash
agent-os mcp list
agent-os mcp register my-server --endpoint https://host/mcp
```

## API registry

`agent-os apis list` shows the curated catalog (HackerNews, Reddit, GitHub,
Wikipedia, Open-Meteo, Serper, Firecrawl, Crunchbase, …) with an evaluation
verdict (score, auth, pricing, rate limits, commercial-use, agent fit). APIs
are discovered through the registry but never called automatically; every call
is a deliberate, logged tool action. Add APIs by extending the catalog or
registering new entries.