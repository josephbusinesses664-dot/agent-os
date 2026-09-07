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
```

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