---
id: implementation-review
name: Implementation Review
description: "Verify an implementation against its requirements and acceptance criteria — with executed evidence."
category: 06-testing
version: 1.1.0
source: agent-os core library (Superpowers review methodology)
license: MIT
capability_type: skill
required_tools: [repo.search, shell.write, browser.open]
risk_level: low
cost_level: low
dependencies: [code-review, testing-strategy]
compatible_agents: [test-engineer, code-reviewer, qa-director]
tags: [review, implementation, verification]
contract:
  prerequisites:
    - "implementation and its requirements/acceptance criteria"
  preferred_agents: [test-engineer, code-reviewer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each acceptance criterion verified by execution or inspection"
  artifact_contract:
    - "implementation review (criteria → evidence → verdict)"
  quality_gates:
    - "every acceptance criterion mapped to evidence"
    - "unverified criteria marked unverified (not assumed)"
  verification:
    - "run tests and exercise the behavior"
  failure_modes:
    assumed_done: "verify, never assume — an unrun check is an open risk"
    scope_creep: "flag behavior outside the criteria"
  escalation:
    - "criteria that cannot be met by the implementation"
  handoff_in:
    - "implementation"
    - "requirements/acceptance criteria"
  handoff_out:
    - "implementation review (criteria → evidence → verdict)"
  evaluation:
    - "criterion-by-criterion verification"
    - "honest unverified marking"
  observability:
    - "record the review verdict"
  related_skills: [code-review, testing-strategy, ui-qa]
---

# Implementation Review

## Purpose
Verify an implementation against its requirements and acceptance criteria —
criterion by criterion, with executed evidence, never assumption.

## When to use / When NOT to use
- use: after implementation, before handoff/merge
- avoid: reviewing without the acceptance criteria; avoid declaring done
  without running anything

## Inputs & assumptions
- inputs: implementation, requirements/acceptance criteria
- assumptions: the criteria are the contract — anything the implementation
  adds beyond them is scope creep to flag

## Workflow
1. List the acceptance criteria.
2. For each criterion, find the evidence: test run, code inspection,
   browser behavior.
3. Execute where feasible (tests, browser); inspect where not.
4. Mark each criterion verified / not-verified / failed, with evidence.
5. Flag scope creep and missing criteria coverage.
6. Produce the verdict.

## Evidence requirements
- Every criterion mapped to evidence; unverified criteria marked
  unverified — an unrun check is an open risk.

## Artifact contract
- `implementation-review`: criteria table (criterion → evidence → status),
  scope notes, verdict.

## Quality gates (definition of done)
- [ ] Every criterion mapped to evidence
- [ ] Unverified criteria honestly marked
- [ ] Verdict consistent with the table

## Verification
- Run tests; exercise the behavior in the browser.

## Failure & recovery
| failure | recovery |
|---|---|
| assumed done | verify; mark honestly |
| scope creep | flag with location |
| unmet criterion | report with evidence; escalate if blocking |

## Escalation
- Criteria the implementation cannot meet — escalate with evidence.

## Handoff
- receives: implementation, requirements
- passes: implementation review (criteria → evidence → verdict)

## Evaluation
The org evaluates this skill by criterion-by-criterion verification and
honest marking of unverified items.

## Observability
- Record the review verdict in the audit trail.

## References
- references/checklist.md — evidence mapping walkthrough