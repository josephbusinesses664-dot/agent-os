---
id: testing-strategy
name: Testing Strategy
description: "Risk-driven test strategy — pyramid, risk analysis, coverage decisions — with justification, not coverage theater."
category: 06-testing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [test-automation]
compatible_agents: [test-engineer, qa-director]
tags: [testing, strategy]
contract:
  prerequisites:
    - "the system/change to test and its risk profile"
  preferred_agents: [test-engineer, qa-director]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "strategy decisions tied to risk, not fashion"
  artifact_contract:
    - "test strategy (levels, focus, risks, exclusions)"
  quality_gates:
    - "unit/integration/e2e split justified by risk"
    - "risky paths identified"
    - "what is NOT tested stated explicitly"
  verification:
    - "check the strategy covers the highest-risk paths"
  failure_modes:
    coverage_theater: "target risk, not percentage"
    e2e_heavy: "push most coverage down the pyramid"
  escalation:
    - "risks that cannot be tested with current infrastructure"
  handoff_in:
    - "system/change"
    - "risk profile"
  handoff_out:
    - "test strategy for planning and automation"
  evaluation:
    - "risk-to-test mapping"
    - "pyramid justification"
  observability:
    - "record the strategy and its rationale"
  related_skills: [test-automation, testing, e2e-testing]
---

# Testing Strategy

## Purpose
Decide what to test, at which level, and why — driven by risk, not
coverage percentages. State explicitly what is NOT tested and why.

## When to use / When NOT to use
- use: before a testing effort, at release boundaries
- avoid: strategy documents disconnected from the actual risk profile;
  avoid chasing coverage numbers

## Inputs & assumptions
- inputs: system/change, risk profile
- assumptions: risk assessment assumed unless evidence exists — label it

## Workflow
1. Identify the highest-risk paths: money, auth, data integrity, external
   contracts, security.
2. Decide the level per risk: unit (logic), integration (contracts),
   e2e (critical journeys) — the pyramid: most coverage low, few e2e.
3. Decide what NOT to test and why (trivial, throwaway, covered upstream).
4. Specify the tools and gates (CI, coverage thresholds with rationale).
5. Produce the strategy.

## Evidence requirements
- Every strategy decision tied to a risk or a stated cost trade-off.

## Artifact contract
- `test-strategy`: risk→level mapping, pyramid split, exclusions with
  reasons, gates.

## Quality gates (definition of done)
- [ ] Unit/integration/e2e split justified by risk
- [ ] Risky paths explicitly covered
- [ ] Exclusions stated
- [ ] Gates defined

## Verification
- Check the highest-risk paths appear in the coverage plan.

## Failure & recovery
| failure | recovery |
|---|---|
| coverage theater | target risk, not percentage |
| e2e-heavy | push coverage down the pyramid |
| unmapped risk | add it to the strategy and plan |

## Escalation
- Risks untestable with current infrastructure — escalate the capability
  gap.

## Handoff
- receives: system, risk profile
- passes: test strategy to planning and automation

## Evaluation
The org evaluates this skill by risk-to-test mapping and pyramid
justification.

## Observability
- Record the strategy and rationale in the project.

## References
- references/patterns.md — risk catalogs and pyramid splits