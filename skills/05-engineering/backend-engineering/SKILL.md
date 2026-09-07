---
id: backend-engineering
name: Backend Engineering
description: "Verification-first backend work — tests, contracts, error handling, auth, observability — minimal safe changes."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, repo.tree, shell.write]
risk_level: medium
cost_level: low
dependencies: [architecture, api-design, database-design]
compatible_agents: [backend-lead, software-architect, database-engineer]
tags: [backend, engineering, api]
contract:
  prerequisites:
    - "requirements/acceptance criteria"
    - "access to the codebase"
  preferred_agents: [backend-lead, software-architect]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "tests run and pass (not claimed)"
    - "contracts validated against the API"
  artifact_contract:
    - "backend implementation + tests + contract notes"
  quality_gates:
    - "tests written and executed for changed paths"
    - "error handling defined for failure paths"
    - "auth/permission checks verified"
    - "observability added (logging/tracing) for new endpoints"
  verification:
    - "run the test suite; run typecheck"
  failure_modes:
    test_failure: "inspect, reproduce, isolate, patch, retest"
    contract_drift: "validate against the API contract"
  escalation:
    - "changes requiring schema migrations with downtime"
  handoff_in:
    - "requirements"
    - "acceptance criteria"
  handoff_out:
    - "implementation + tests + known risks"
  evaluation:
    - "test pass/fail (real execution)"
    - "error handling quality"
  observability:
    - "trace model/tool calls; record test results"
  related_skills: [api-design, database-design, testing-strategy, architecture]
---

# Backend Engineering

## Purpose
Implement backend work verification-first: tests actually run, contracts
validate, error paths are handled, auth is checked, and observability
exists — with minimal safe changes unless requirements demand more.

## When to use / When NOT to use
- use: any backend implementation or fix
- avoid: rewriting working code without a requirement (prefer minimal safe
  changes)

## Inputs & assumptions
- inputs: requirements/acceptance criteria, codebase
- assumptions: label assumptions about scale, concurrency, and security
  boundaries

## Workflow
1. Explore the relevant code (repo.search/repo.tree); find existing
   patterns and follow them.
2. Plan the minimal change that meets the requirements.
3. Implement, including error paths and validation.
4. Write tests for changed paths (unit + integration where warranted).
5. Run tests and typecheck; fix until green.
6. Check auth/permission paths and data correctness.
7. Add observability (structured logs, tracing) for new endpoints.
8. Document known risks in the handoff.

## Evidence requirements
- Test results from actual execution — "should work" is not evidence.

## Artifact contract
- `backend-implementation`: changed files, tests, contract notes, known
  risks.

## Quality gates (definition of done)
- [ ] Tests written and executed for changed paths
- [ ] Error handling defined
- [ ] Auth/permission checks verified
- [ ] Typecheck passes
- [ ] Observability added

## Verification
- Run the full relevant test suite and typecheck; record results.
- Validate API changes against the contract.

## Failure & recovery
| failure | recovery |
|---|---|
| test failure | inspect → reproduce → isolate → patch → retest |
| contract drift | validate against the API contract |
| schema migration risk | plan migration path; escalate if downtime required |

## Escalation
- Changes requiring downtime or destructive migrations — escalate for
  approval.

## Handoff
- receives: requirements, acceptance criteria
- passes: implementation, tests, known risks, test results

## Evaluation
The org evaluates this skill by real test pass/fail, error-handling
quality, and contract validity.

## Observability
- Trace tool/model calls and record test results in the audit trail.

## References
- references/patterns.md — error-handling and validation patterns