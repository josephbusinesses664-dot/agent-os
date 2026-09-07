---
id: model-selection
name: Model Selection
description: Choose the right model per task — complexity, cost, capability, availability.
category: 15-ai
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [models, routing, cost]
compatible_agents: [ai-engineer, cto]
---

# Model Selection

## Purpose
Route work to the cheapest model that demonstrably suffices — treat premium
models as a scarce resource.

## Tiering
| Tier | Use for | Example |
|---|---|---|
| t0 deterministic | no LLM needed — code, transformations | file ops, math |
| t1 cheap workers | classification, extraction, summarization, routine | DeepSeek Flash |
| t2 senior workers | coding, architecture assistance, research, debugging | DeepSeek Pro |
| t3 executive | strategy, hard reasoning, major reviews, high risk | Claude-class |

## Decision inputs
Task complexity, risk, importance, reasoning needed, context size, latency
needs, remaining budget, availability.

## Rules
- Escalate only when the task warrants it; a cheaper model that passes the
  eval is the correct choice.
- Failover chains are mandatory: primary → fallback → emergency → human.
- Track cost per task and review routing decisions with data (see evaluation
  skill).