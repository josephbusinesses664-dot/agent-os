# Security

## Model

1. **Least privilege** — every agent has an explicit permission map; anything
   that can escape the sandbox (shell, deploy, github, API calls) defaults to
   deny and is granted per role.
2. **Sandbox** — file tools operate inside the per-project workspace; path
   escapes are blocked (`PermissionError`) and every write is audit-logged.
3. **Approval gates** — high-risk stages (deployments) and high-risk tools
   (`shell`) require explicit human approval. No approval record, no execution.
4. **Audit trail** — every significant action records who/what/when/why/
   project/task/tool/model/result. Queryable via CLI, API and admin UI.
5. **Secrets** — never in code, configs, images or logs; env vars only.
   `.env` is git-ignored; `.env.example` documents everything.
6. **Capability provenance** — every imported skill/MCP server records
   source, license, dependencies, required permissions and risk; anything
   external is treated as untrusted until reviewed.
7. **Validation** — inputs validated at the API boundary (pydantic schemas);
   tool args validated by handlers; output validated by the audit/result flow.

## Permission reference

| Tool | Default | Notes |
|---|---|---|
| filesystem.read | allow | sandbox only |
| filesystem.write | allow | sandbox only, audited |
| web.search | allow | |
| memory.* / project.state | allow | |
| mattermost.post | allow | identity-prefixed |
| web.scrape / api.call | deny | granted to research roles |
| shell | deny | high risk → approval required |
| deploy / github | deny | granted to deployment/devops roles; stages still approval-gated |
| mcp.call | deny | granted per server |

## Approval flow

1. An agent wants to do something risky → an `ApprovalRequest` is created and
   the task pauses (`awaiting_approval`).
2. The request surfaces in Mattermost (`approvals` channel), the admin UI and
   `agent-os approvals list`.
3. Human decides: `@agent approve <id>` / `@agent reject <id>` / CLI / UI.
4. Approved → execution proceeds (tool re-attempted, or the paused workflow
   resumes from its checkpoint). Rejected → the stage/workflow fails with a
   recorded decision.

## Known limitations

- The admin UI has no built-in auth — protect it with a reverse proxy /
  basic auth or keep it on a private network.
- The REST API is unauthenticated by default (it exposes operational data,
  not secrets). Wire an auth proxy before exposing it publicly.
- Secrets for third-party APIs are held in env vars at the process level;
  for stricter isolation, run agents/workers in separate containers with
  scoped env.
- MCP stdio transport is not yet wired (streamable-HTTP is). Any MCP server
  is treated as high risk until evaluated.