---
id: e2e-testing
name: End-to-End Testing
description: "End-to-end testing — real user journeys through a real browser, with evidence of execution."
category: 06-testing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot, browser.click, browser.type, browser.evaluate, shell.write]
risk_level: medium
cost_level: medium
dependencies: [testing-strategy, ui-qa]
compatible_agents: [test-engineer, ui-qa]
tags: [e2e, testing, browser]
contract:
  prerequisites:
    - "a running app (or the ability to start it)"
    - "the user journeys to verify"
  preferred_agents: [test-engineer, ui-qa]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "each journey executed and its outcome recorded"
  artifact_contract:
    - "e2e results (journeys, steps, pass/fail, evidence)"
  quality_gates:
    - "primary journeys executed in a real browser"
    - "error/edge paths included"
    - "failures reproduced and diagnosed"
  verification:
    - "run each journey; capture state at assertion points"
  failure_modes:
    flaky: "stabilize waits/selectors; isolate from real network where possible"
    app_down: "start the app or escalate the environment"
  escalation:
    - "blocking defects found"
  handoff_in:
    - "running app"
    - "journeys"
  handoff_out:
    - "e2e results with evidence and defect reports"
  evaluation:
    - "journeys actually executed"
    - "defects correctly diagnosed"
  observability:
    - "record steps and outcomes per journey"
  related_skills: [testing-strategy, ui-qa, test-automation]
---

# End-to-End Testing

## Purpose
Verify real user journeys in a real browser — executing, not asserting —
with evidence of each step and outcome.

## When to use / When NOT to use
- use: release-critical journeys, after integration, UI-heavy changes
- avoid: unit-level logic (that belongs in unit tests); avoid claiming e2e
  coverage without running the browser

## Inputs & assumptions
- inputs: running app, user journeys
- assumptions: environment state (data, network) assumed and recorded so
  results are reproducible

## Workflow
1. Identify the journeys that must work (from acceptance criteria).
2. Start the app; confirm it loads.
3. Execute each journey in the browser step by step (browser.open →
   snapshot → click/type → evaluate assertions).
4. Include error and edge paths (validation, cancel, empty).
5. Record pass/fail with evidence at assertion points.
6. Diagnose failures: reproduce, isolate, classify.

## Evidence requirements
- Each journey executed; outcome recorded with the state at assertion
  points.

## Artifact contract
- `e2e-results`: journeys, steps, pass/fail, evidence, defect reports.

## Quality gates (definition of done)
- [ ] Primary journeys executed in a real browser
- [ ] Error/edge paths included
- [ ] Failures diagnosed, not listed
- [ ] Environment state recorded

## Verification
- Run each journey; capture the state where assertions happen.

## Failure & recovery
| failure | recovery |
|---|---|
| flaky test | stabilize waits/selectors; isolate network |
| app down | start it or escalate the environment |
| real defect | reproduce, diagnose, report with evidence |

## Escalation
- Blocking defects — escalate with reproduction steps.

## Handoff
- receives: running app, journeys
- passes: e2e results with evidence and defect reports

## Evaluation
The org evaluates this skill by journeys actually executed and defects
correctly diagnosed.

## Observability
- Record steps and outcomes per journey in the audit trail.

## References
- references/patterns.md — stable-selector and wait patterns