---
id: test-automation
name: Test Automation
description: "Automated tests that stay green — strategy, stability, failure classification, maintenance — with executed evidence."
category: 06-testing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell.write, repo.search]
risk_level: low
cost_level: low
dependencies: [testing-strategy]
compatible_agents: [test-engineer]
tags: [testing, automation, ci]
contract:
  prerequisites:
    - "behavior to lock in and the test framework in use"
  preferred_agents: [test-engineer]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "test runs executed and results recorded"
  artifact_contract:
    - "automated tests + run results + stability notes"
  quality_gates:
    - "tests deterministic (no sleeps/flaky waits)"
    - "failures classified (product bug vs test bug)"
    - "meaningful assertions (not smoke-only)"
  verification:
    - "run the suite multiple times to check stability"
  failure_modes:
    flaky: "stabilize; a flaky suite erodes trust"
    brittle: "assert behavior, not implementation details"
  escalation:
    - "test infrastructure failures blocking the pipeline"
  handoff_in:
    - "behavior"
    - "framework"
  handoff_out:
    - "tests + results + maintenance notes"
  evaluation:
    - "determinism (repeated runs)"
    - "assertion quality"
  observability:
    - "record run results"
  related_skills: [testing-strategy, testing, e2e-testing]
---

# Test Automation

## Purpose
Write automated tests that stay green: deterministic, behavior-asserting,
and maintainable — with executed evidence and failure classification.

## When to use / When NOT to use
- use: locking in behavior that regresses easily
- avoid: test noise (asserting implementation details); avoid smoke tests
  that assert nothing meaningful

## Inputs & assumptions
- inputs: behavior, test framework
- assumptions: the framework and conventions come from the project — read
  them, don't assume

## Workflow
1. Identify the behavior to lock in and its risky edges.
2. Write tests asserting behavior (inputs → observable outputs/effects).
3. Keep them deterministic: no sleeps, stable selectors, isolated data.
4. Run the suite; classify failures (product bug vs test bug) and fix.
5. Run repeatedly to confirm stability.
6. Record results and maintenance notes.

## Evidence requirements
- Test runs executed with results recorded.

## Artifact contract
- `automated-tests`: tests, run results, stability notes, failure
  classifications.

## Quality gates (definition of done)
- [ ] Tests deterministic
- [ ] Failures classified, not ignored
- [ ] Assertions meaningful
- [ ] Suite stable across repeated runs

## Verification
- Run the suite multiple times; record stability.

## Failure & recovery
| failure | recovery |
|---|---|
| flaky test | stabilize; fix the root cause |
| brittle test | assert behavior, not internals |
| suite slowdown | parallelize/prioritize; keep fast feedback |

## Escalation
- Test infrastructure failures blocking the pipeline.

## Handoff
- receives: behavior, framework
- passes: tests, results, maintenance notes

## Evaluation
The org evaluates this skill by determinism across runs and assertion
quality.

## Observability
- Record run results in the audit trail.

## References
- references/patterns.md — determinism and stability patterns