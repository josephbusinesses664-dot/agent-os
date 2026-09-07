---
id: performance-review
name: Performance Review
description: "Measured performance review — budgets, profiling, hotspots — with numbers, not opinions."
category: 06-testing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.evaluate, shell.write]
risk_level: low
cost_level: low
dependencies: [frontend-engineering, backend-engineering]
compatible_agents: [performance-reviewer, test-engineer]
tags: [performance, profiling]
contract:
  prerequisites:
    - "a performance budget or stated concern"
    - "the environment to measure in"
  preferred_agents: [performance-reviewer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "measurements recorded (numbers), not impressions"
  artifact_contract:
    - "performance review (budget, measurements, hotspots, fixes)"
  quality_gates:
    - "budget stated before measuring"
    - "hotspots identified from measurements"
    - "fixes tied to measurements"
  verification:
    - "re-measure after fixes to confirm improvement"
  failure_modes:
    opinion: "re-anchor on numbers"
    wrong_scope: "measure the right tier (mobile counts)"
  escalation:
    - "budget violations blocking release"
  handoff_in:
    - "budget"
    - "environment"
  handoff_out:
    - "performance review with measured findings"
  evaluation:
    - "measurement quality"
    - "fix effectiveness (re-measured)"
  observability:
    - "record measurements"
  related_skills: [frontend-engineering, motion-engineering, backend-engineering]
---

# Performance Review

## Purpose
Review performance with measurements, not opinions: state the budget,
measure, find hotspots, fix, re-measure.

## When to use / When NOT to use
- use: before release with a budget, when perf is a stated concern
- avoid: declaring performance "fine" without numbers; avoid measuring only
  the fast path on a fast machine

## Inputs & assumptions
- inputs: budget, environment
- assumptions: target tier and measurement conditions recorded so results
  are comparable

## Workflow
1. State the budget (LCP, FPS, latency, payload) before measuring.
2. Measure on the target tier (mobile counts) with browser.evaluate and
   network/profiler tools.
3. Identify hotspots from the measurements.
4. Propose fixes tied to measured hotspots.
5. Apply and re-measure; confirm the improvement.

## Evidence requirements
- Numbers recorded for every claim; the environment recorded.

## Artifact contract
- `performance-review`: budget, measurements, hotspots, fixes,
  before/after numbers.

## Quality gates (definition of done)
- [ ] Budget stated before measuring
- [ ] Hotspots measurement-derived
- [ ] Fixes verified by re-measurement

## Verification
- Re-measure after fixes; record before/after.

## Failure & recovery
| failure | recovery |
|---|---|
| opinion-based | re-anchor on numbers |
| wrong tier | measure the real target |
| fix ineffective | iterate; escalate the trade |

## Escalation
- Budget violations blocking release — escalate with measurements.

## Handoff
- receives: budget, environment
- passes: performance review with measured findings

## Evaluation
The org evaluates this skill by measurement quality and fix effectiveness
(re-measured).

## Observability
- Record measurements and environment in the audit trail.

## References
- references/patterns.md — measurement methodology and common hotspots