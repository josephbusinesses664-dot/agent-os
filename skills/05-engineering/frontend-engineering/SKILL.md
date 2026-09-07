---
id: frontend-engineering
name: Frontend Engineering
description: "Production-grade frontend — typecheck, lint, tests, accessibility, responsive states, performance — verified."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, repo.tree, browser.open, browser.snapshot, browser.evaluate, shell.write]
risk_level: medium
cost_level: medium
dependencies: [ui-design, accessibility, performance-review]
compatible_agents: [frontend-lead, ui-engineer, react-nextjs]
tags: [frontend, react, ui, engineering]
contract:
  prerequisites:
    - "design/UX input (or clear requirements)"
    - "access to the codebase"
  preferred_agents: [frontend-lead, ui-engineer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "typecheck/lint/test output recorded"
    - "browser verification of key states"
  artifact_contract:
    - "frontend implementation + verified states + perf notes"
  quality_gates:
    - "typecheck passes"
    - "lint passes"
    - "tests pass (run, not claimed)"
    - "accessibility checked (keyboard, contrast, reduced motion)"
    - "responsive states verified in browser"
    - "loading/error/empty states present"
  verification:
    - "run typecheck/lint/tests; inspect in browser per state"
  failure_modes:
    build_failure: "read the error, fix the root cause, rebuild"
    ui_regression: "check the affected states in the browser"
  escalation:
    - "requirements impossible within performance budget"
  handoff_in:
    - "design/UX input"
    - "requirements"
  handoff_out:
    - "implementation + test results + perf notes"
  evaluation:
    - "real verification results"
    - "state coverage"
    - "performance sanity"
  observability:
    - "record build/test results and browser checks"
  related_skills: [ui-design, react-nextjs, accessibility, ui-qa, testing-strategy]
---

# Frontend Engineering

## Purpose
Build production-quality interfaces verification-first: typecheck, lint,
tests, accessibility, responsive and interaction states, performance —
with evidence, not claims.

## When to use / When NOT to use
- use: any frontend implementation
- avoid: generic template-looking output; avoid shipping without the
  verification gates below

## Inputs & assumptions
- inputs: design/UX input, requirements, codebase
- assumptions: browser support and device targets assumed unless stated

## Workflow
1. Explore the codebase; follow existing component/state patterns.
2. Translate the design into hierarchy, states, responsive behavior.
3. Implement loading/error/empty states for every data view.
4. Write tests for the meaningful behavior (not snapshot noise).
5. Run typecheck, lint, tests — fix until green.
6. Verify in a real browser: key states, keyboard nav, responsive widths,
   reduced motion.
7. Performance sanity: no obvious jank, assets sized, no render leaks.
8. Hand off with verification evidence.

## Evidence requirements
- Typecheck/lint/test output recorded in the handoff.
- Browser checks performed for key states.

## Artifact contract
- `frontend-implementation`: changed files, test results, browser
  verification notes, known risks.

## Quality gates (definition of done)
- [ ] Typecheck passes
- [ ] Lint passes
- [ ] Tests pass (executed)
- [ ] Loading/error/empty states present
- [ ] Accessibility checks done (keyboard, contrast, reduced motion)
- [ ] Responsive states verified in browser

## Verification
- Run the gates; inspect the built UI per state with browser tools.

## Failure & recovery
| failure | recovery |
|---|---|
| build failure | read the error, fix the root cause, rebuild |
| UI regression | check affected states in browser |
| perf issue | profile, fix the hotspot, re-measure |

## Escalation
- Requirements impossible within the performance budget — escalate the
  trade.

## Handoff
- receives: design/UX input, requirements
- passes: implementation, test results, browser verification, perf notes

## Evaluation
The org evaluates this skill by real verification results, state coverage,
and performance sanity — a pretty but unverified UI fails.

## Observability
- Record build/test results and browser checks in the audit trail.

## References
- references/checklist.md — the frontend verification gate walkthrough