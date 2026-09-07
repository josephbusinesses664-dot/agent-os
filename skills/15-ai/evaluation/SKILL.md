---
id: evaluation
name: Agent Evaluation
description: Evaluate agents and skills — golden sets, regression, cost, reliability.
category: 15-ai
version: 1.0.0
source: agent-os core library (Superpowers review + eval methodology)
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [evaluation, evals, quality]
compatible_agents: [ai-engineer, qa-director]
---

# Agent Evaluation

## Purpose
Measure whether agents/skills actually improve: task completion, correctness,
cost, tool discipline, hallucination, reliability.

## Dimensions
1. **Task completion** — did the agent finish the task? (verified artifacts)
2. **Correctness** — is the output right? (review score, tests, human check)
3. **Efficiency** — steps/tool calls/tokens to complete; did it waste calls?
4. **Cost** — actual spend vs. budget; model-tier appropriateness.
5. **Tool discipline** — used permitted tools; no invented results; errors
   reported truthfully.
6. **Hallucination** — unverifiable claims, fabricated evidence.
7. **Reliability** — success rate across runs; variance.

## Method
- **Golden set** — 10-30 representative tasks with known-good outputs;
  score on a rubric; track over time (prompt/model changes must not regress).
- **Regression** — re-run golden set on every prompt/model change.
- **Field evaluation** — sample real runs weekly; classify failures.

## Skill evaluation
Usefulness, reliability, compatibility, security, cost, duplication, quality
— disable skills that repeatedly fail or that no agent actually uses.

## Rules
- An agent without evaluation data is unmanaged. Report numbers, not vibes.
- Evaluate the system it runs in, not just the model: routing, context,
  tools all matter.