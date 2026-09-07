# Admin UI

The web console (served at `/` by the control plane, http://localhost:8300)
gives you a full picture of the organization. Mattermost remains the primary
communication surface; the UI is for inspection and governance.

## Views

- **Overview** — stat cards (agents, tasks, projects, skills, models, spend),
  live agent status table, recent events.
- **Health** — per-service health with latency and details.
- **Agents** — the org chart flattened to a table: id, role, parent, model
  tier, state, risk, allowed tools; filter by id/role.
- **Tasks** — status filter; shows agent, model, cost and dependencies.
- **Projects** — status, stage, workflow, cost/budget, artifact count.
- **Skills** — all 100 skills with category, state and required tools.
- **Models** — tiers, pricing, context, fallbacks.
- **MCP & APIs** — registered MCP servers + the API catalog with evaluation
  verdicts.
- **Budget** — spend bars per scope + usage records.
- **Approvals** — approve/reject right from the UI.
- **Events / Audit** — live event feed and the audit log.

Auto-refreshes every 6 seconds. Single-file, dependency-free, dark theme,
responsive (collapses to an icon rail on mobile) — no gratuitous animation.

## API

All views are plain JSON endpoints under `/api/*` (`/api/status`,
`/api/agents`, `/api/tasks`, `/api/projects`, `/api/skills`, `/api/models`,
`/api/mcp`, `/api/apis`, `/api/budget`, `/api/usage`, `/api/events`,
`/api/audit`, `/api/approvals`, `/api/memory`, `/api/messages`,
`/api/health`) plus mutation endpoints: `POST /api/goals`,
`POST /api/approvals/{id}/decide`, `POST /api/tasks/{id}/run`, etc.