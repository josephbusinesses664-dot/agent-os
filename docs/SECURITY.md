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
| postgres.query / docker | deny | read-only adapters, granted to db/devops roles; postgres also approval-gated |
| browser.* | deny | granted to research/design/QA/frontend roles; `browser.evaluate` is high-risk |
| agent.delegate | deny | only a child's parent (or explicit grant) may delegate |
| mcp.call | deny | granted per server |

Every tool not explicitly granted **defaults to deny** for agents created
ad-hoc (CLI/API) — least privilege is enforced in the executor, not just in
prompts. The org-chart agents carry explicit grants.

## Credential isolation

- MCP credentials set via `POST /api/mcp/{name}/credentials` live only in
  process memory, are never persisted to the store, and never appear in
  serialized server output (`public_dict()` redacts token material).
- A new credential forces a fresh MCP client for that server (no stale auth).
- External adapters (GitHub/Postgres/Docker) are read-only by construction:
  the read-only gate runs *before* any connection or config check.

## Approval flow

1. An agent wants to do something risky → an `ApprovalRequest` is created and
   the task pauses (`awaiting_approval`).
2. The request surfaces in Mattermost (`approvals` channel), the admin UI and
   `agent-os approvals list`.
3. Human decides: `@agent approve <id>` / `@agent reject <id>` / CLI / UI.
4. Approved → execution proceeds (tool re-attempted, or the paused workflow
   resumes from its checkpoint). Rejected → the stage/workflow fails with a
   recorded decision.

## Memory permission-scoping

Memory access is enforced in code (`agentos/memory/scoping.py`), not by prompt
etiquette. `ScopedMemoryStore` wraps the memory store for the runtime tools:

| Scope | Read | Write |
|---|---|---|
| `agent` | the agent itself + its parent (supervision) | the agent itself |
| `task` | task participants: assignee, assignee's parent, agents whose parent is the assignee | assignee + its parent |
| `project` | agents operating in that project (system-supplied context) | same |
| `org` | everyone | autonomy L4+ (directors/executives) |
| `user` | never (agents have no path to user-private memories) | never |

Possession of a task object is not participation: an unassigned task has no
participants, and an executive holding a task reference gains nothing.
Denied recalls return an **empty result** (existence is never disclosed) and
are audit-logged as `memory.recall_denied` / `memory.save_denied`.

## Rollback / compensation ledger

Every successful mutative tool call (`shell`, `api.call`, `mcp.call`,
`mattermost.post`, `deploy`, `github`, `docker`, `filesystem.write`,
`file.patch`) is recorded (`agentos/security/rollback.py`) with an honest
reversibility classification:

- `reversible` — a compensation is registered and executable (workspace
  writes: the compensation deletes the written file, confined to the
  recorded workspace base)
- `compensating` — no true undo, but harm-reducing action recorded
- `irreversible` — no compensation known; recorded so the system can warn
  and gate before acting, not apologize after

Rollback is idempotent, ordered per task (newest first, stops at first
failure), and never stores secrets (args are redacted). The admin Control
Plane view and `POST /api/rollback/{id}/rollback` let a human execute or
inspect compensations.

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