---
id: quality-gates
name: Quality Gates
description: Define and enforce quality gates between workflow stages.
category: 12-operations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [quality, gates, workflow]
compatible_agents: [qa-director, operations-director, project-manager]
---

# Quality Gates

## Purpose
Prevent bad work from flowing downstream: each stage has an exit criterion
that must be met before the next stage starts.

## Gate design
For each gate: **condition** (verifiable), **owner** (who verifies), **escalation**
(what happens on failure).

Example pipeline gates:
```
RESEARCH COMPLETE   → strategy review (evidence quality)
STRATEGY APPROVED   → executive sign-off
PRD APPROVED        → requirements traceable + testable
ARCHITECTURE APPROVED → trade-offs recorded, security considered
IMPLEMENTATION      → typecheck, lint, tests pass (real runs)
SECURITY PASS       → no critical/high findings
FINAL REVIEW        → review score ≥ threshold
DEPLOYMENT APPROVAL → human approval (high risk)
```

## Rules
- Gates are binary: pass or fail with evidence; no "kind of passes".
- Automated gates (tests, lint) run automatically; human gates have owners
  and deadlines.
- A gate that never fails is either working perfectly or decorative — check.