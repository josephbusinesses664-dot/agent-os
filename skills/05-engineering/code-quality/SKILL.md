---
id: code-quality
name: Code Quality
description: "The code-quality bar — clarity, tests, error handling, naming — with machine-verifiable gates."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, shell.write]
risk_level: low
cost_level: low
dependencies: [testing-strategy, code-review]
compatible_agents: [software-architect, backend-lead, frontend-lead, code-reviewer]
tags: [code-quality, standards]
contract:
  prerequisites:
    - "code under review or to be written"
  preferred_agents: [code-reviewer, software-architect]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "gates verified by execution (lint/typecheck/tests)"
  artifact_contract:
    - "quality assessment (gate results, findings)"
  quality_gates:
    - "no dead code or silent exception swallowing"
    - "meaningful names; no magic constants"
    - "errors handled or explicitly propagated"
    - "tests exist for non-trivial logic"
  verification:
    - "run lint/typecheck/tests and record results"
  failure_modes:
    silent_swallowing: "replace bare excepts with explicit handling"
    hidden_state: "surface state and side effects"
  escalation:
    - "quality issues in security-critical paths"
  handoff_in:
    - "code"
  handoff_out:
    - "quality assessment with findings"
  evaluation:
    - "gate results (real execution)"
    - "finding precision"
  observability:
    - "record gate results"
  related_skills: [code-review, testing-strategy, implementation-review]
---

# Code Quality

## Purpose
Apply a machine-verifiable quality bar: lint/typecheck/tests pass, no dead
code, no silent exception swallowing, meaningful names, deliberate state.

## When to use / When NOT to use
- use: before merging any non-trivial change
- avoid: gate theater — run the gates, don't assert them

## Inputs & assumptions
- inputs: code
- assumptions: the project's lint/type/test conventions are read from the
  project config, not assumed

## Workflow
1. Read the change in context.
2. Run the project gates (lint, typecheck, tests) and record results.
3. Review for: dead code, silent excepts, magic constants, hidden state,
   duplicated logic, unclear names.
4. For each finding: location, why it matters, fix.
5. Produce the assessment.

## Evidence requirements
- Gate results from actual execution.

## Artifact contract
- `quality-assessment`: gate results, findings (location, reason, fix).

## Quality gates (definition of done)
- [ ] Gates pass (executed)
- [ ] No silent exception swallowing
- [ ] No dead code
- [ ] No magic constants
- [ ] Non-trivial logic has tests

## Verification
- Run the gates; record output.

## Failure & recovery
| failure | recovery |
|---|---|
| silent swallowing | replace with explicit handling |
| hidden state | surface state and side effects |
| gate failure | fix the root cause; re-run |

## Escalation
- Quality issues in security-critical paths.

## Handoff
- receives: code
- passes: quality assessment with findings

## Evaluation
The org evaluates this skill by executed gate results and finding
precision.

## Observability
- Record gate results in the audit trail.

## References
- references/checklist.md — quality gate walkthrough