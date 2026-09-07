---
id: operations-strategy
name: Operations Strategy
description: Design delivery operations — process, tooling, cadence, quality gates.
category: 12-operations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [operations, process, delivery]
compatible_agents: [operations-director, project-manager]
---

# Operations Strategy

## Purpose
Design the delivery system: how work flows from request to shipped result,
with quality gates and feedback loops.

## Elements
1. **Workflow** — the path a request takes (intake → plan → execute → review →
   ship); each step has an owner and an input/output contract.
2. **Quality gates** — automated checks + human review at the stages where
   mistakes are expensive (requirements, architecture, security, deploy).
3. **Cadence** — regular reviews (daily status, weekly decisions); short
   enough to catch drift.
4. **Tooling** — automation for everything repetitive: task dispatch, testing,
   reporting, approvals.
5. **Feedback loops** — failures feed process improvement; evaluations feed
   agent improvement.

## Rules
- Process exists to make quality repeatable — if a step doesn't catch errors
  or add value, cut it.
- Bottlenecks are process bugs: find the stage where work waits, fix it.
- Everything critical is monitored; everything significant is audited.