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
budget policy, explicit permission map (least privilege), memory scope,
risk level, and a structured **identity**. Definitions live in
`agentos/agents/hierarchy.py` (and can be overridden via the registry or
CLI).

## Agent identity (cognitive layer)

Every built-in agent carries an `AgentIdentity` (`agentos/agents/identities.py`):

| Field | Meaning | Consumed by |
|---|---|---|
| `archetype` | cognitive pattern: executive / architect / researcher / product / designer / engineer / qa / security / operations / sales / marketing | prompt composition |
| `mission` | the one question this agent owns (role boundaries) | prompt composition |
| `priorities` | ranked, first = highest | prompt composition |
| `decision_framework` | ordered questions the agent applies | prompt composition |
| `risk_tolerance` | minimal / low / moderate / high | routing + judgment |
| `autonomy` | L0 recommend-only … L5 executive-within-policy | prompt composition |
| `evidence_standard` | what counts as proof for this role | prompt composition |
| `quality_standard` | the bar the agent holds work to | prompt composition |
| `anti_patterns` | behaviors the agent refuses | prompt composition |
| `communication_style` / `disagreement_style` / `escalation_policy` / `failure_behavior` | how the agent talks, disagrees, escalates, recovers | prompt + challenge protocol |

The identity renders as an operational block in every agent prompt (see
`identity_prompt_block`). It is judgment, not authority: **identity never
overrides permissions, budgets or approval gates.** An agent claiming to be
the CEO gains nothing.

Autonomy levels: L0 recommend only · L1 reversible low-risk actions ·
L2 routine project actions · L3 multi-step tasks in approved scope ·
L4 coordinate/delegate across agents · L5 executive decisions within policy.
Dangerous external actions still require explicit approval regardless of
level.

Role boundaries (each agent owns exactly one question): product-researcher
asks "what do customers need?", market-researcher "what is happening in the
market?", competitor-analyst "how are alternatives positioned?", product-
manager "what should we build?", software-architect "how should it be
built?", qa-director "does it actually work?", security-reviewer "can it be
abused?", executive "is the initiative worth doing?".

## Structured disagreement (challenges)

Agents disagree through first-class challenge objects, not chat noise:

```
agent.challenge:  {agent, concern, claim, evidence[], severity,
                   recommended_action, scope}
agent.resolve:    {challenge_id, verdict: accept|reject|escalate,
                   rationale}   # rejection requires a rationale
```

Challenges carry evidence and severity; `blocking`/`high` challenges emit
`agent.challenge` events. Resolution is bounded — the recipient (or its
parent) decides and a DECISION message records the verdict, so the
organization moves on instead of debating forever.

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