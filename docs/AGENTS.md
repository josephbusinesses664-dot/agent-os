# Agents

## The organization

The default org chart has 41 agent definitions — executives, directors and
specialists across product, engineering, design, research, marketing, sales,
QA and operations. Agents are *definitions*, not processes: the orchestrator
instantiates one for the duration of a task and returns it to idle.

```
Executive Director
├── Chief of Staff
├── Product Director → PM, Requirements Analyst, Product Researcher
├── CTO → Architect, Frontend Lead, Backend Lead, DB Engineer, DevOps, AI Engineer
├── Design Director → UX, UI, Design Systems, Motion/Creative
├── Research Director → Market, Community, Competitor, Technical Researchers
├── Marketing Director → SEO, Content, Social, Growth
├── Sales Director → Lead Research, Sales Analyst, Outreach
├── QA Director → Test Engineer, Code Reviewer, Security Reviewer, Perf Reviewer
└── Operations Director → PM, Documentation, Deployment, Monitoring
```

## Agent definition

Each agent carries: id/name/role/description, parent + allowed children,
recommended skills, permitted tools, model policy (tier + max tier),
budget policy, explicit permission map (least privilege), memory scope and
risk level. Definitions live in `agentos/agents/hierarchy.py` (and can be
overridden via the registry or CLI).

## Permissions

Permissions are per-tool and default to *deny* for anything that can escape
the sandbox:

- Research agents: web search/scrape, read, memory — **no** shell/deploy/API.
- Deployment agent: shell + deploy + github — production actions still require
  human approval.
- Executive: reads broadly, writes selectively, high-risk actions gated.

Every tool call is checked against the agent's permission map and recorded in
the audit log. Tool execution is confined to the project workspace.

## Spawning / delegation

An agent requests a sub-agent by creating a delegated task. The engine
enforces: max recursion depth (default 4), max parallel agents (default 8),
duplicate-task detection while a task is active, and per-task budget checks.
Depth like `CTO → Frontend Lead → UI Engineer → Animation Specialist` is
supported; unbounded fan-out is prevented.

## Model policies

Each agent declares a default tier: executives/CTO t3 (Claude-class where
available), senior workers t2 (DeepSeek Pro / GLM), routine workers t1
(DeepSeek Flash / GLM Flash), and anything mechanical t0 (no LLM). The router
may escalate by complexity (bounded by the agent's max tier) or downgrade on
budget pressure.

## Agent-to-agent communication

Agents use structured messages (`task_request`, `task_result`, `question`,
`escalation`, `approval`, …) with sender/recipient/project/task/priority and a
persisted payload — not just natural-language chat. Decisions are recorded in
the project decision log.

## Human override

From Mattermost: `@agent stop <id>`, `@agent pause <id>`, `@agent resume <id>`,
`@agent status`, `@agent explain`, `@agent retry <task>`, `@agent approve <id>`,
`@agent reject <id>`, `@agent escalate`. Human instructions take priority over
scheduled work; paused agents are skipped.