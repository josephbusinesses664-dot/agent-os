# Mattermost

Mattermost is the human-facing interface of the AI organization. You talk to
the whole agency from chat; the admin UI and CLI are for inspection and
governance.

## Setup

1. Have a Mattermost server (or create one at https://mattermost.com).
2. Create a bot account → System Console → Personal Access Tokens → create a
   token for it.
3. Set `MATTERMOST_URL` and `MATTERMOST_TOKEN` in `.env`.
4. `agent-os start` — the listener connects, creates the team
   (`ai-agency` by default) and the workspace channels automatically.

## Workspace layout

```
AI ORGANIZATION
├── announcements, executive, decisions
├── approvals            ← approval requests + approve/reject commands
├── agent-status         ← live agent status board
├── agent-logs           ← task reports and artifacts
├── agent-discussion
├── system-errors, monitoring, security, deployments
└── project-<id>*        ← per-project channels (created on demand)
```

## Agent identity layer

One bot account, many agents: every post carries the internal identity of the
agent that wrote it.

```
[CLAUDE • CTO]
Architecture completed. Trade-offs recorded in the decision log.

[DEEPSEEK PRO • FRONTEND LEAD]
Frontend implementation ready for review — 14 tests passed (see report).
```

## Commands

```
I want to build a new SaaS product.    → executive creates a project + workflow
@agent status                          → status board
@agent explain                         → command help
@agent stop cto | @agent pause cto     → human override (agent skipped)
@agent resume cto                      → resume
@agent retry <task_id>                 → re-queue a failed task
@agent approve <approval_id>           → grant a high-risk action
@agent reject <approval_id>            → reject (workflow fails at that stage)
```

## How it works

The listener polls channels (REST, robust behind proxies — no WebSocket
dependency) and routes messages: `@agent` commands, `@approve/@reject`
shortcuts, and anything else in the general channel is treated as a goal for
the executive. System events are routed to channels automatically
(`approval.requested` → approvals, `workflow.failed` → system-errors, …).

## Resilience

Mattermost is optional: if it's down or unconfigured, the system keeps
working and the post attempts are logged. The platform remains fully usable
through the CLI and admin UI.