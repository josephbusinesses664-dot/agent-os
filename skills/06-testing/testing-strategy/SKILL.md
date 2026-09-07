---
id: testing-strategy
name: Testing Strategy
description: Design the test approach for a project — what to test, at which level, how to gate.
category: 06-testing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [testing, strategy, coverage]
compatible_agents: [qa-director, test-engineer]
---

# Testing Strategy

## Purpose
Decide what gets tested, at what level, and what blocks shipping — so the
testing budget goes where risk lives.

## Method
1. **Risk map** — the failures that hurt most (money, data, security, core
   UX, integrations). Test depth follows risk.
2. **Levels** — unit (logic), integration (boundaries: DB, APIs, providers),
   e2e (critical paths). Each level has a job; don't compensate for a missing
   level with more of another.
3. **Gate definition** — what must pass before merge/deploy; automated where
   possible.
4. **Testability** — architecture must support tests (injection, boundaries,
   no hidden globals) — fix testability problems early.
5. **Regression discipline** — every bug fix ships with a failing-then-passing
   test.
6. **Measurement** — review: are tests catching real regressions? (mutation
   testing occasionally, not coverage worship)

## Rules
- Coverage percentages are a floor, not a goal — test behavior that matters.
- A test suite that takes an hour and catches nothing is worse than no suite:
  fix the strategy, not the volume.