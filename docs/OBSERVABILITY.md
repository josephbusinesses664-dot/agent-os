# Observability

## Events

Every significant action publishes an event (persisted, queryable):

```
agent.created/started/completed/failed
task.created/started/completed/failed
review.created/completed
approval.requested/granted/rejected
deployment.started/completed/failed
model.requested/completed · model.failover
skill.loaded · tool.called · mcp.called
workflow.started/completed/failed · project.created
budget.warning
```

`agent-os events` tails them; the admin UI shows a live feed; the Mattermost
listener routes them to channels.

## Audit log

Append-only record of every significant action: actor, action, target,
project/task/tool/model, result, details. `agent-os audit` queries it.

## Health

`agent-os health` (or `GET /api/health`) checks: database, kv, queue,
orchestrator (LangGraph compiled), worker, model providers, MCP registry,
skill registry, agent registry, memory and Mattermost — with latency and a
clear ok/degraded/down status.

## Budget & usage

`agent-os budget status`, `/api/budget`, `/api/usage`: spend per scope with
limits, and per-call usage records (model, tokens, cost, project/agent/task).
`budget.warning` fires at 90% of a limit.

## Logs

Structured logs carry run/task/project context; the control plane writes to
stdout (capture with your log collector). No silent exception swallowing —
errors are logged, classified, associated with their task/project/agent and
surfaced via events.

## Status board

`agent-os status` and the admin UI Overview show: agents available/active/idle,
skills/tools/models/MCP counts, projects/tasks, approvals pending, and
monthly spend — the "AI AGENCY ONLINE" view from the spec.