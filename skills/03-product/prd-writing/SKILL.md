---
id: prd-writing
name: PRD Writing
description: "Product requirements document — problem, users, requirements with rationale, acceptance criteria, metrics, scope."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [requirements-analysis, acceptance-criteria, user-stories]
compatible_agents: [product-manager, requirements-analyst]
tags: [prd, requirements, product]
contract:
  prerequisites:
    - "research/opportunity context (why this product)"
    - "target users and the problem to solve"
  preferred_agents: [product-manager, requirements-analyst]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "requirements traceable to problem statements"
    - "each requirement testable via acceptance criteria"
  artifact_contract:
    - "PRD (problem, users, requirements, acceptance criteria, metrics, scope)"
  quality_gates:
    - "every requirement has rationale + acceptance criteria"
    - "out-of-scope list present"
    - "metrics defined for success"
  verification:
    - "read each requirement: is it testable? is the rationale non-obvious?"
  failure_modes:
    requirements_bloat: "prune to the MVP spine; park the rest in a backlog section"
    untraceable: "re-link each requirement to a problem or user need"
  escalation:
    - "requirements that contradict research evidence"
  handoff_in:
    - "opportunity context"
    - "target users"
  handoff_out:
    - "PRD with requirements + acceptance criteria to engineering"
  evaluation:
    - "requirement testability"
    - "problem-to-requirement traceability"
  observability:
    - "store the PRD as a project artifact"
  related_skills: [requirements-analysis, user-stories, acceptance-criteria, product-strategy]
---

# PRD Writing

## Purpose
Produce a product requirements document that connects problem → users →
requirements → acceptance criteria → metrics, with scope discipline.

## When to use / When NOT to use
- use: before engineering starts on a product or major feature
- avoid: for trivial tasks; avoid writing a PRD with no problem statement —
  that is a feature list, not a PRD

## Inputs & assumptions
- inputs: opportunity context, target users, problem
- assumptions: label every assumption about users and behavior; requirements
  built on assumptions inherit them

## Workflow
1. **Problem** — the user problem, with evidence (research, signals).
2. **Users & journey** — who, what job, the journey the product changes.
3. **Requirements** — numbered, each with: rationale, priority,
   dependencies, edge cases, failure behavior.
4. **Acceptance criteria** — per requirement (see acceptance-criteria skill).
5. **Metrics** — the success metrics and how they will be measured.
6. **Scope** — MVP spine, out-of-scope list, future backlog.
7. **Review** — check traceability and testability; challenge any requirement
   whose rationale is "because it was asked for".

## Evidence requirements
- Every requirement traces to a problem or user need.
- Metrics are measurable (counted, not vibes).

## Artifact contract
- `PRD`: problem, users/journey, requirements (with rationale/priority/
  dependencies/edge cases/failure behavior), acceptance criteria, metrics,
  scope.

## Quality gates (definition of done)
- [ ] Every requirement has rationale + acceptance criteria
- [ ] Out-of-scope list present
- [ ] Success metrics defined
- [ ] Requirements trace to problems

## Verification
- Read each requirement as an engineer: is it testable?
- Read the scope: does the MVP spine deliver the core job?

## Failure & recovery
| failure | recovery |
|---|---|
| requirements bloat | prune to the MVP spine; park the rest |
| untraceable requirements | re-link to problems or user needs |
| contradictory requirements | surface the contradiction, escalate |

## Escalation
- Requirements that contradict research evidence — escalate with the
  evidence on both sides.

## Handoff
- receives: opportunity context, target users
- passes: PRD with requirements + acceptance criteria to engineering and QA

## Evaluation
The org evaluates this skill by requirement testability and
problem-to-requirement traceability.

## Observability
- Store the PRD as a project artifact linked to the project and task.

## References
- references/patterns.md — requirement-writing patterns and common PRD gaps