---
id: ui-qa
name: UI QA
description: "Automated UI QA gate — HTML validity, asset resolution, console errors, runtime checks — verified in a real browser."
category: 06-testing
version: 1.1.0
source: agent-os core library (UI QA gate methodology)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot, browser.evaluate, browser.screenshot]
risk_level: low
cost_level: low
dependencies: [e2e-testing, frontend-engineering]
compatible_agents: [ui-qa, test-engineer]
tags: [qa, ui, browser]
contract:
  prerequisites:
    - "a built page or app to verify"
  preferred_agents: [ui-qa, test-engineer]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "check results recorded (validity, assets, console)"
  artifact_contract:
    - "ui-qa report (checks, failures, severity, fixes)"
  quality_gates:
    - "HTML validity checked"
    - "all assets resolve"
    - "zero console errors"
    - "key states verified in browser"
  verification:
    - "load the page; collect console and network results"
  failure_modes:
    console_error: "reproduce, fix, reload, confirm clean"
    broken_asset: "fix the path/reference; re-verify"
  escalation:
    - "blocking UI defects"
  handoff_in:
    - "built page"
  handoff_out:
    - "ui-qa report with evidence"
  evaluation:
    - "checks actually run"
    - "failure diagnosis quality"
  observability:
    - "record check results"
  related_skills: [e2e-testing, accessibility, frontend-engineering]
---

# UI QA

## Purpose
Run the automated QA gate over built UI: HTML validity, asset resolution,
console errors, and key runtime states — verified in a real browser with
evidence.

## When to use / When NOT to use
- use: after any site/page/frontend build, before calling it done
- avoid: QA by reading code alone — load the page

## Inputs & assumptions
- inputs: built page
- assumptions: target browser/device recorded with the results

## Workflow
1. Load the page in a real browser.
2. Collect console messages and network results (browser.evaluate,
   network requests).
3. Check: zero console errors; all assets resolve; HTML validity;
   key states render.
4. For each failure: reproduce, diagnose, record severity.
5. Fix and re-verify; produce the report.

## Evidence requirements
- Check results recorded (console, network, validity) — the evidence is
  the load, not the claim.

## Artifact contract
- `ui-qa-report`: checks run, failures (severity, diagnosis, fix),
  verification evidence.

## Quality gates (definition of done)
- [ ] HTML validity checked
- [ ] All assets resolve
- [ ] Zero console errors
- [ ] Key states verified

## Verification
- Load the page and collect console/network evidence.

## Failure & recovery
| failure | recovery |
|---|---|
| console error | reproduce → fix → reload → confirm clean |
| broken asset | fix the reference; re-verify |
| missing state | implement and re-check |

## Escalation
- Blocking UI defects — escalate with evidence.

## Handoff
- receives: built page
- passes: ui-qa report with evidence

## Evaluation
The org evaluates this skill by checks actually run and failure diagnosis
quality.

## Observability
- Record check results in the audit trail.

## References
- references/checklist.md — the UI QA gate walkthrough