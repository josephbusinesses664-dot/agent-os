# Models & Routing

## Tier system

| Tier | Use for | Example models |
|---|---|---|
| t0 | deterministic — no LLM (code/tools) | — |
| t1 | cheap workers: classification, extraction, summarization, routine research | deepseek-flash, glm-flash, local |
| t2 | senior workers: coding, research, debugging, analysis | deepseek-pro, glm-pro |
| t3 | executive: strategy, architecture, hard reasoning, major reviews, high risk | claude-sonnet-4-5 |

Models are defined in the Model Registry (id, provider, name, tier, context,
price per 1M tokens, capabilities, fallbacks). Defaults are the *starting
policy* — nothing is hardcoded into the router.

## Router

`route(agent, task)` considers: task complexity (keyword + length heuristic),
risk, importance, agent role policy (tier + max tier), budget state and model
availability. It escalates within the agent's tier bounds, downgrades on
budget pressure (`AUTO_DOWNGRADE_ON_BUDGET`), and always produces a
human-readable reason.

## Failover

```
primary model → fallback chain → cheaper-tier emergency → human escalation
```

A provider outage never kills a workflow: `_call_with_failover` walks the
model's fallback chain, then any available cheaper tier, emits a
`model.failover` event, and only surfaces an error when nothing is available.

## Resource discipline

- **Claude is premium** — reserved for executive decisions, architecture,
  difficult bugs/reviews, and high-risk judgment. The system operates on
  cheaper models when premium capacity is unavailable.
- **DeepSeek is the workhorse** — Pro for senior work, Flash for high-volume.
- The **Budget Manager** records every call (provider, model, tokens, cost,
  project/agent/task) against global/daily/project/agent/task limits and
  triggers `budget.warning` at 90%.

## Cost tracking

`agent-os budget status`, the admin UI Budget tab, and the `/api/usage`
endpoint show spend per scope. Costs are estimated from token usage × price
table (the provider SDKs don't return billing; estimates are labeled as such).