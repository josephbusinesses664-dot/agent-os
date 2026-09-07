---
id: architecture
name: Software Architecture
description: System architecture — boundaries, modules, data flow, trade-offs, decisions.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [architecture, design, tradeoffs]
compatible_agents: [cto, software-architect]
---

# Software Architecture

## Purpose
Design the structure of a system so it is understandable, testable and
extensible — and record the trade-offs that shaped it.

## Method
1. **Constraints first** — scale needs, team shape, deployment targets, budget,
   regulatory. Architecture serves constraints; don't invent scale.
2. **Boundaries** — separate interface / control / domain / data; each module
   has one reason to change; dependencies point inward.
3. **Data flow** — draw the flow of a request and a background job end-to-end;
   identify failure points and consistency requirements.
4. **Contracts** — interfaces between modules are the architecture; define them
   explicitly, version them.
5. **Trade-off table** — for each significant decision: options, pros, cons,
   decision, and what would reverse it.
6. **Extensibility** — plugin/registry patterns where capability sets grow
   (models, skills, tools); avoid coupling core to specific providers.

## Rules
- YAGNI vs extensibility: abstract where the system is *known* to vary
  (providers, skills), not everywhere.
- An architecture you can't test is a guess — design for testability.
- Record every significant decision in the decision log with alternatives.