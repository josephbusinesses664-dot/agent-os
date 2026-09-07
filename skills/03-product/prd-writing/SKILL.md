---
id: prd-writing
name: PRD Writing
description: Write precise product requirement documents from research and strategy — problem, users, scope, success metrics.
category: 03-product
version: 1.0.0
source: agent-os core library (Superpowers-style specification)
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [prd, requirements, product]
compatible_agents: [product-manager, product-director]
---

# PRD Writing

## Purpose
Turn a validated opportunity into a specification that engineers can build
against and QA can verify. The PRD is the contract.

## PRD structure
1. **Problem** — the user problem and evidence it is real.
2. **Users** — who this is for; personas with jobs-to-be-done.
3. **Goals & non-goals** — what this release does and explicitly does not.
4. **Success metrics** — the 1-3 metrics that prove value (not vanity).
5. **Scope** — features in, features out, with rationale.
6. **Requirements** — numbered, testable; each states the behavior and the
   acceptance criteria.
7. **Edge cases** — empty states, errors, permission limits, offline.
8. **Open questions** — decided later; each with an owner.

## Writing rules
- Requirements must be testable: "the system SHALL…" statements that a test
  can pass/fail. No vague "should be nice" language.
- Tie every requirement to a user need or metric; cut requirements without one.
- Version the PRD; record decisions and changes in the decision log.

## Output
PRD markdown artifact saved to the project workspace under `artifacts/`.