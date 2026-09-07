---
id: react-nextjs
name: React / Next.js
description: "React/Next.js engineering — component architecture, state, performance, SSR correctness — verified."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, repo.tree, shell.write, browser.open, browser.evaluate]
risk_level: medium
cost_level: medium
dependencies: [frontend-engineering]
compatible_agents: [frontend-lead, ui-engineer]
tags: [react, nextjs, typescript]
contract:
  prerequisites:
    - "requirements and the codebase"
    - "framework version confirmed from the project"
  preferred_agents: [frontend-lead, ui-engineer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "typecheck/test output recorded"
    - "SSR/CSR behavior verified where relevant"
  artifact_contract:
    - "React/Next implementation + verification results"
  quality_gates:
    - "typecheck passes"
    - "state management chosen deliberately (not by default)"
    - "no hydration mismatches"
    - "effects cleaned up (no leaks)"
    - "performance: no obvious re-render storms"
  verification:
    - "run typecheck/tests; check console for hydration errors"
  failure_modes:
    hydration_mismatch: "align server/client rendering paths"
    rerender_storm: "memoize/restructure; verify with profiling"
  escalation:
    - "architecture choices that fight the framework"
  handoff_in:
    - "requirements"
    - "codebase"
  handoff_out:
    - "implementation + verification results + known risks"
  evaluation:
    - "real verification results"
    - "framework-idiomatic patterns"
  observability:
    - "record build/test results"
  related_skills: [frontend-engineering, ui-design, testing-strategy]
---

# React / Next.js

## Purpose
Implement React/Next.js features framework-idiomatically: deliberate state
management, clean effects, correct SSR/CSR behavior, and performance —
verified by typecheck, tests, and the browser console.

## When to use / When NOT to use
- use: React/Next.js work in this codebase
- avoid: inventing patterns that fight the framework; avoid adding state
  libraries where local state suffices

## Inputs & assumptions
- inputs: requirements, codebase
- assumptions: framework version and conventions read from the actual
  project — never assumed from memory

## Workflow
1. Confirm framework version and existing patterns (repo.search).
2. Choose state scope deliberately: local → context → server state — in
   that order of preference.
3. Implement components with clean effects; every subscription/observer
   cleaned up.
4. Handle SSR/CSR boundaries (no window at render time unless guarded).
5. Write tests for behavior.
6. Run typecheck/tests; check the browser console for hydration errors.
7. Performance: check for obvious re-render storms; profile if needed.

## Evidence requirements
- Typecheck/test output recorded.
- Hydration/console clean verified in the browser.

## Artifact contract
- `react-implementation`: changed files, state decisions, test results,
  known risks.

## Quality gates (definition of done)
- [ ] Typecheck passes
- [ ] Tests pass
- [ ] No hydration mismatches (console-verified)
- [ ] Effects cleaned up
- [ ] State management deliberate

## Verification
- Run the gates; load the page and check the console.

## Failure & recovery
| failure | recovery |
|---|---|
| hydration mismatch | align server/client render paths; retest |
| re-render storm | memoize/restructure; profile to confirm |
| effect leak | add cleanup; verify unmount behavior |

## Escalation
- Choices that fight the framework — escalate the architecture trade.

## Handoff
- receives: requirements, codebase
- passes: implementation, verification results, known risks

## Evaluation
The org evaluates this skill by real verification results and
framework-idiomatic patterns.

## Observability
- Record build/test results and console checks.

## References
- references/patterns.md — state-scope decisions and effect patterns