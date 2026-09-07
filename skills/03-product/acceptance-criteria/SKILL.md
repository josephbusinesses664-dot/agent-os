---
id: acceptance-criteria
name: Acceptance Criteria
description: "Testable acceptance criteria — rationale, edge cases, failure behavior, verification — for every requirement."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [requirements-analysis, user-stories]
compatible_agents: [product-manager, requirements-analyst, test-engineer]
tags: [acceptance, criteria, testing, gherkin]
contract:
  prerequisites:
    - "a requirement or user story to make testable"
  preferred_agents: [product-manager, requirements-analyst]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each criterion observable and machine-checkable where possible"
  artifact_contract:
    - "acceptance criteria set (given/when/then, edge cases, failure behavior)"
  quality_gates:
    - "every criterion is unambiguous and testable"
    - "happy path + at least one edge case + failure behavior covered"
  verification:
    - "read each criterion: could two engineers disagree on pass/fail?"
  failure_modes:
    vague_criteria: "rewrite with concrete inputs and expected outputs"
    untestable: "split into observable sub-criteria"
  escalation:
    - "requirements where criteria expose a missing product decision"
  handoff_in:
    - "requirement or user story"
  handoff_out:
    - "acceptance criteria with edge cases for engineering and QA"
  evaluation:
    - "criteria testability (deterministic pass/fail)"
    - "edge-case and failure coverage"
  observability:
    - "link criteria to the requirement and the task"
  related_skills: [requirements-analysis, user-stories, testing-strategy]
---

# Acceptance Criteria

## Purpose
Turn requirements into unambiguous, testable acceptance criteria — including
edge cases and failure behavior — so "done" is a deterministic decision.

## When to use / When NOT to use
- use: before implementation, whenever a requirement enters a task
- avoid: for research/strategy artifacts (no behavior to test); avoid
  criteria so vague no test could use them

## Inputs & assumptions
- inputs: requirement or user story
- assumptions: state assumed inputs/context the criteria depend on

## Workflow
1. Restate the requirement as observable behavior.
2. Write the happy path as given/when/then with concrete inputs and expected
   outputs.
3. Add edge cases: empty/missing input, boundaries, duplicates, permissions,
   concurrency, timeouts.
4. Add failure behavior: what happens on error, and what the user sees.
5. Add verification notes: how each criterion can be checked (unit,
   integration, browser, manual).
6. Review: could two engineers disagree on pass/fail for any criterion?

## Evidence requirements
- Every criterion is observable and, where possible, machine-checkable —
  "works well" is not a criterion; "returns ≤200ms at 100 concurrent
  requests" is.

## Artifact contract
- `acceptance-criteria`: per-requirement given/when/then, edge cases,
  failure behavior, verification method.

## Quality gates (definition of done)
- [ ] Every criterion unambiguous and testable
- [ ] Happy path + ≥1 edge case + failure behavior covered
- [ ] Concrete inputs and expected outputs present
- [ ] Verification method stated per criterion

## Verification
- Read each criterion as a tester would: is pass/fail deterministic?
- Check edge cases cover the risky inputs, not just the convenient ones.

## Failure & recovery
| failure | recovery |
|---|---|
| vague criteria | rewrite with concrete inputs/outputs |
| untestable criteria | split into observable sub-criteria |
| criteria exposing a product gap | flag the missing decision, escalate |

## Escalation
- Criteria that expose an unresolved product decision (undefined
  permissions, undefined error UX) — escalate with the question.

## Handoff
- receives: requirement or user story
- passes: acceptance criteria + edge cases + failure behavior to engineering
  and QA

## Evaluation
The org evaluates this skill by criteria testability and edge/failure
coverage — criteria are judged by whether a test can pass or fail them.

## Observability
- Record the criteria with the requirement and task so QA can verify
  against the same set.

## References
- references/patterns.md — edge-case catalogs by feature type