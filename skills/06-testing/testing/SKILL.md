---
id: testing
name: Testing Discipline
description: "The testing discipline — execute, don't claim — with failure injection and regression coverage."
category: 06-testing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell.write, repo.search]
risk_level: low
cost_level: low
dependencies: [testing-strategy, test-automation]
compatible_agents: [test-engineer]
tags: [testing, verification]
contract:
  prerequisites:
    - "behavior to verify"
  preferred_agents: [test-engineer]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "test executions recorded with outcomes"
  artifact_contract:
    - "test report (cases, outcomes, coverage notes)"
  quality_gates:
    - "tests executed, not asserted"
    - "negative and edge cases included"
    - "regression set maintained"
  verification:
    - "run and record; rerun after fixes"
  failure_modes:
    claim_only: "execute — 'should work' is not a test result"
    happy_path_only: "add negative and edge cases"
  escalation:
    - "failures that block the deliverable"
  handoff_in:
    - "behavior"
  handoff_out:
    - "test report with executed outcomes"
  evaluation:
    - "execution evidence"
    - "edge coverage"
  observability:
    - "record test outcomes"
  related_skills: [test-automation, testing-strategy, e2e-testing]
---

# Testing Discipline

## Purpose
The core discipline: tests are executed and recorded, never claimed.
Include negative and edge cases; keep a regression set.

## When to use / When NOT to use
- use: whenever a deliverable claims to work
- avoid: reporting "should work" as a result — run it

## Inputs & assumptions
- inputs: behavior to verify
- assumptions: environment state recorded so results are reproducible

## Workflow
1. Identify the behavior and its risky edges.
2. Write/select tests: happy path + negative + edge cases.
3. Execute; record outcomes per case.
4. Fix failures, re-run, record.
5. Update the regression set with any newly found bugs.

## Evidence requirements
- Executions recorded with outcomes — the evidence is the run, not the
  claim.

## Artifact contract
- `test-report`: cases, outcomes, environment, regression notes.

## Quality gates (definition of done)
- [ ] Tests executed with recorded outcomes
- [ ] Negative and edge cases included
- [ ] Regression set maintained

## Verification
- Run and record; re-run after fixes.

## Failure & recovery
| failure | recovery |
|---|---|
| claim-only | execute |
| happy-path-only | add the negative/edge cases |
| flaky | stabilize and re-run |

## Escalation
- Failures blocking the deliverable — escalate with evidence.

## Handoff
- receives: behavior
- passes: test report with executed outcomes

## Evaluation
The org evaluates this skill by execution evidence and edge coverage.

## Observability
- Record test outcomes in the audit trail.

## References
- references/checklist.md — negative/edge case catalogs