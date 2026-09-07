---
id: accessibility
name: Accessibility
description: "Accessibility as an engineering requirement — keyboard, screen reader, contrast, reduced motion, with verification."
category: 04-design
version: 1.1.0
source: agent-os core library (MengTo design methodology)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [ui-design, frontend-engineering]
compatible_agents: [ui-designer, frontend-lead, ui-qa, accessibility]
tags: [accessibility, wcag, a11y]
contract:
  prerequisites:
    - "a built interface (or design) to evaluate"
  preferred_agents: [ui-qa, frontend-lead]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "verification results per check (passed / failed with location)"
  artifact_contract:
    - "accessibility report (checks, findings, severity, fixes)"
  quality_gates:
    - "full keyboard operability"
    - "visible focus states"
    - "contrast meets WCAG AA for text"
    - "reduced-motion respected"
    - "screen-reader labels on interactive elements"
  verification:
    - "tab through the full interface with a browser"
    - "check contrast numerically, not by eye"
    - "toggle prefers-reduced-motion and confirm no seizure-risk motion"
  failure_modes:
    focus_trap: "restore natural tab order; check escape paths"
    missing_labels: "add aria-labels / programmatic labels"
  escalation:
    - "critical flows unusable by keyboard or screen reader"
  handoff_in:
    - "built interface or design"
  handoff_out:
    - "accessibility report with severity-ranked findings"
  evaluation:
    - "correct identification of real violations (few false positives)"
    - "verification-based, not assumption-based"
  observability:
    - "record findings and their verification method"
  related_skills: [ui-qa, frontend-engineering, ui-design]
---

# Accessibility

## Purpose
Enforce accessibility as an engineering requirement: keyboard operability,
screen-reader semantics, contrast, reduced motion — verified, not assumed.

## When to use / When NOT to use
- use: on every interface before it ships; when auditing existing UIs
- avoid: claiming accessibility without running the checks below; avoid
  treating a11y as a late "polish" step

## Inputs & assumptions
- inputs: built interface or design
- assumptions: target level is WCAG 2.1 AA unless stated otherwise — record
  the target

## Checks (all must be verified)
1. **Keyboard** — every interactive element reachable and operable by Tab;
   no focus traps; visible focus indicator.
2. **Contrast** — text meets WCAG AA (4.5:1 normal, 3:1 large); check
   numerically.
3. **Semantics** — landmarks, headings hierarchy, one h1, correct roles.
4. **Labels** — every form control has a programmatic label; icon-only
   buttons have aria-labels.
5. **Reduced motion** — `prefers-reduced-motion` respected; no flashing
   above seizure thresholds.
6. **Responsive + zoom** — no content loss at 200% zoom or 320px width.
7. **Screen reader** — primary flows make sense when read linearly.

## Workflow
1. Load the interface in a browser (browser.open/browser.snapshot).
2. Walk the checks above, recording pass/fail with the location for each
   failure.
3. Classify severity: critical (flow blocked) / major / minor.
4. For each finding: location, why it fails, and the fix.
5. Produce the report.

## Evidence requirements
- Every finding has a verification method and a location — no "probably
  accessible" claims.

## Artifact contract
- `accessibility-report`: target level, checks table (pass/fail, location,
  severity), fixes, residual risks.

## Quality gates (definition of done)
- [ ] Full keyboard operability verified by tabbing
- [ ] Focus states visible
- [ ] Contrast numeric-checked to AA
- [ ] Reduced-motion respected (no seizure-risk motion)
- [ ] Interactive elements labeled

## Verification
- Tab through every control in a real browser.
- Compute contrast ratios from actual colors.
- Toggle reduced motion and confirm behavior changes.

## Failure & recovery
| failure | recovery |
|---|---|
| focus trap | restore natural tab order; add escape path |
| missing labels | add programmatic labels; retest |
| contrast fail | adjust colors; re-measure numerically |

## Escalation
- Critical flows unusable by keyboard or screen reader — escalate as a
  release blocker, not a backlog item.

## Handoff
- receives: built interface or design
- passes: accessibility report (severity-ranked findings + fixes) to
  engineering

## Evaluation
The org evaluates this skill by correct identification of real violations
(not false positives) and by verification-based evidence.

## Observability
- Record findings and their verification method in the audit trail.

## References
- references/checklist.md — full WCAG AA check walkthrough