---
id: tech-decision
name: Technology Decisions
description: Structured evaluation and selection of technology, libraries and services.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
tags: [decisions, evaluation, technology]
compatible_agents: [cto, software-architect, ai-engineer]
---

# Technology Decisions

## Purpose
Select technologies with evidence and record the decision so future agents
don't relitigate it.

## Evaluation rubric
Score each candidate 0-5 on:
1. **Fit** — does it solve the actual problem?
2. **Maturity** — age, adoption, maintenance activity, release stability.
3. **Ecosystem** — docs, community, tooling, talent availability.
4. **Operability** — deploy, monitor, debug, upgrade paths.
5. **Security** — track record, dependency posture, supply-chain risk.
6. **Cost** — license, infra, and migration cost.
7. **Extensibility** — does it lock us in or compose well?

## Process
1. Research ≥ 3 candidates (official docs; check maintenance, not just stars).
2. Score each; note dealbreakers (license, security, maturity).
3. Recommend one with: primary choice, alternatives, migration/exit path.
4. Record in the decision log with alternatives and reasoning.

## Rules
- Prefer boring technology for core paths; experiment only where isolated.
- "Industry standard" is evidence, not a conclusion — check it's still true.
- Every dependency is a liability: justify additions.