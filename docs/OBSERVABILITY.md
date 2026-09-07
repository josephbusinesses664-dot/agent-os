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

## Traces

Every meaningful action records a **span** into the trace store
(`agentos/observability/trace.py`): kind (`agent | stage | model | tool |
evaluator`), trace_id (task id), parent_span, tokens, cost, latency,
status and error class. A task trace is the replayable chain
agent → stage → model → tool → result → evaluator.

- `/api/traces/<task_id>` or `agent-os traces <task_id>` shows the chain
- `trace.span` events stream to subscribers (Mattermost sink, admin UI)
- `agent-os status` reports total spans and errors

## Evaluation & performance

Every completed stage/task is scored (deterministic evidence checklist,
optionally blended with an LLM judge) and the score feeds the agent's
performance stats: success rate, avg cost, avg latency, tool efficiency,
review score. These stats are **operational** — the model router bumps weak
performers to stronger tiers, and delegation prefers the best track record.

- `agent-os leaderboard [--metric success_rate|avg_cost|tool_efficiency]`
- `agent-os evaluate <dataset>` runs a regression benchmark end-to-end
- `/api/leaderboard`, `/api/evaluation`, `/api/performance`

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