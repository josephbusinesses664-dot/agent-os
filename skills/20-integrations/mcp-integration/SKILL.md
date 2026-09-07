---
id: mcp-integration
name: MCP Integration
description: Connect and govern MCP servers — registry, permissions, risk, credentials.
category: 20-integrations
version: 1.0.0
source: agent-os core library (MCP ecosystem methodology)
license: MIT
capability_type: skill
required_tools: []
risk_level: medium
cost_level: low
tags: [mcp, tools, integration]
compatible_agents: [ai-engineer, devops-engineer]
---

# MCP Integration

## Purpose
Connect MCP servers into the capability registry with governance: only
authorized agents see only authorized tools.

## Process
1. **Evaluate** — the server's source, license, maintenance, and what it can
   touch (files, shell, network, credentials). Untrusted until reviewed.
2. **Register** — name, description, transport (streamable-http/stdio),
   endpoint, tool list, permissions, risk level, required credentials.
3. **Scope tools** — expose only the tools the org actually uses; don't import
   every tool "because it's there".
4. **Permissions** — map tools to agent roles: research agents don't get
   deploy/DB-write tools.
5. **Credentials** — keys via env; never in registry definitions; required
   credentials documented.
6. **Verify** — initialize the server, list tools, call one safe tool, check
   the audit trail records the call.

## Governance
- Every MCP tool call is audited (who, when, args, result).
- High-risk tools require approval just like built-in risky tools.
- Disabled servers stop surfacing immediately (no hot reload needed).

## Rules
- An MCP server with shell/deploy tools is high risk by default — treat it so.
- If a capability exists as a built-in tool, don't add an MCP duplicate.