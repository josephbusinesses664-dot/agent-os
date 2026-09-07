---
id: design-quality
name: Design Quality
description: "The design-quality bar — hierarchy, typography, spacing, color, motion discipline. Design quality is an engineering requirement."
category: 04-design
version: 1.1.0
source: agent-os core library (adapted from MengTo/design methodology + impeccable review criteria)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [ui-design, visual-hierarchy]
compatible_agents: [design-director, ui-designer, frontend-lead, motion-engineer]
tags: [design, quality, polish]
contract:
  prerequisites:
    - "an interface to judge (built or designed)"
    - "the product intent to judge against"
  preferred_agents: [design-director, ui-designer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each critique tied to a concrete element and principle"
  artifact_contract:
    - "design-quality review (strengths, issues ranked, fixes)"
  quality_gates:
    - "hierarchy, spacing, typography, color and motion each evaluated"
    - "every issue tied to a principle, not taste"
    - "states covered: hover, focus, loading, empty, error"
  verification:
    - "inspect the built interface; verify issues in the browser"
  failure_modes:
    taste_review: "re-anchor on principles and user goals"
    missing_states: "check all interaction states before approving"
  escalation:
    - "quality gaps that block launch"
  handoff_in:
    - "interface"
    - "product intent"
  handoff_out:
    - "design-quality review with ranked issues and fixes"
  evaluation:
    - "issues are principle-grounded, not subjective"
    - "state coverage completeness"
  observability:
    - "record the review verdict and issues in the project"
  related_skills: [ui-design, ux-design, visual-hierarchy, design-review]
---

# Design Quality

## Purpose
Apply a consistent quality bar so interfaces read as one deliberate system —
evaluated against principles and product intent, not taste.

## When to use / When NOT to use
- use: before shipping any interface; when reviewing design work
- avoid: reviewing without the product intent (quality is judged against
  intent); avoid praising or damning without concrete elements

## Inputs & assumptions
- inputs: interface, product intent
- assumptions: state the target quality tier if the product does not demand
  the highest tier (internal tool vs consumer landing)

## Quality dimensions (all evaluated)
1. **Hierarchy** — one clear focal point per view; visual weight matches
   information importance.
2. **Spacing** — consistent scale; related elements grouped; whitespace
   intentional.
3. **Typography** — size/weight hierarchy, line length, readable contrast.
4. **Color** — limited purposeful palette; color never the only signal.
5. **Motion** — communicates state/hierarchy or is absent; reduced-motion
   safe.
6. **States** — hover, focus, active, loading, empty, error all designed.

## Workflow
1. Load the interface and the product intent.
2. Walk each quality dimension, recording concrete observations (element,
   principle, gap).
3. Check all interaction states.
4. Rank issues by impact on the user goal.
5. Produce the review with fixes.

## Evidence requirements
- Every critique names the element and the principle it violates — "this
  feels off" is not a finding.

## Artifact contract
- `design-quality-review`: strengths, issues (element, principle, severity,
  fix), state coverage, verdict.

## Quality gates (definition of done)
- [ ] All five dimensions evaluated
- [ ] Every issue principle-grounded
- [ ] All interaction states checked
- [ ] Verdict matches the evidence

## Verification
- Inspect the built interface in a browser and confirm each issue.
- Re-check the states after any fix.

## Failure & recovery
| failure | recovery |
|---|---|
| taste-based review | re-anchor on principles and user goals |
| missing states | check all states before approving |
| conflicting feedback | prioritize issues by impact on the user goal |

## Escalation
- Quality gaps blocking launch — escalate with the specific issues.

## Handoff
- receives: interface, product intent
- passes: design-quality review with ranked issues and fixes

## Evaluation
The org evaluates this skill by whether issues are principle-grounded and
state coverage is complete — subjective praise is not a passing review.

## Observability
- Record the verdict and issue list in the project audit trail.

## References
- references/checklist.md — the full quality-dimension walkthrough