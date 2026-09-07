---
id: user-stories
name: User Stories
description: Write INVEST-quality user stories with acceptance criteria from requirements.
category: 03-product
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [user-stories, agile, backlog]
compatible_agents: [product-manager, requirements-analyst]
---

# User Stories

## Purpose
Decompose requirements into stories a team can size, schedule and verify.

## Story format
```
As a <role>, I want <capability>, so that <outcome>.
```
- Role: who benefits (not job title — the user type).
- Capability: the behavior, one action.
- Outcome: the value, measurable where possible.

## INVEST checklist
- **I**ndependent (can be scheduled alone)
- **N**egotiable (details open until implementation)
- **V**aluable (delivers user value)
- **E**stimable (team can size it)
- **S**mall (fits one iteration)
- **T**estable (clear pass/fail)

## Acceptance criteria
Given/when/then format, minimum 2-3 per story covering the happy path,
an edge case, and a failure path.

## Rules
- Stories describe *what*, not *how* (no implementation details).
- Split stories by value and risk, not by tech layers.
- Every story traces back to a PRD requirement or a metric.