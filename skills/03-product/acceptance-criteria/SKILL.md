---
id: acceptance-criteria
name: Acceptance Criteria
description: Write given/when/then acceptance criteria that QA can execute verbatim.
category: 03-product
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [acceptance, criteria, qa]
compatible_agents: [requirements-analyst, product-manager, test-engineer, qa-director]
---

# Acceptance Criteria

## Purpose
Define done: the observable conditions that prove a feature works.

## Format (Given/When/Then)
```
Given <precondition>
When <action>
Then <observable outcome>
```

## Coverage requirements
Every story needs criteria for:
1. **Happy path** — the primary flow works.
2. **Edge case** — at least one boundary (empty, maximum, special chars, duplicate).
3. **Failure path** — what happens on error/timeout/denied, and the message shown.
4. **Permissions** — behavior for unauthorized users where applicable.

## Quality checks
- Each criterion is atomic (one condition per Then).
- Testable without implementation knowledge.
- No "should" — only observable statements.
- Deterministic — same input → same expected output.

## Rules
- Criteria are the QA contract; tests trace to criteria.
- If a criterion is hard to test, the requirement is probably ambiguous — go fix it.