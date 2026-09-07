---
id: ai-engineering
name: AI Engineering
description: Building agentic systems — prompts, tool use, context management, evaluations, cost control.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [ai, agents, llm]
compatible_agents: [ai-engineer, cto]
---

# AI Engineering

## Principles
1. **Deterministic where possible** — validation, parsing, idempotency,
   retries are code, not prompts. Use the LLM only for judgment work.
2. **Prompt as code** — versioned, testable; changes go through review like
   code changes.
3. **Context discipline** — send only relevant context (progressive disclosure);
   large context is not free — it costs latency, tokens and attention.
4. **Tool use** — narrow tools with clear contracts; permission boundaries;
   results fed back explicitly; never let the model invent tool results.
5. **Failover & fallbacks** — provider outage ≠ system outage; degrade tiers,
   queue, escalate to human.
6. **Cost control** — route by complexity; track spend per model/agent/task;
   prefer the cheapest model that demonstrably suffices.
7. **Evaluation** — golden-set evals per behavior; regression suite for
   prompts; measure hallucination, not just pass rates.
8. **Honesty** — never claim executed actions without evidence (test output,
   deployment result). Truthful state over impressive UI.

## Agent system design
- System prompt = role + authority + limitations + escalation path + quality
  bar + output format.
- Structured messaging between agents; persisted decisions; memory that
  distinguishes fact from noise.