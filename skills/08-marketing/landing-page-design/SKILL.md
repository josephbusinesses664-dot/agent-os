---
id: landing-page-design
name: Landing Page Design
description: "Intent-first landing pages — value, proof, one CTA, conversion flow — with browser verification."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot, browser.evaluate]
risk_level: low
cost_level: low
dependencies: [copywriting, ui-design, conversion-optimization]
compatible_agents: [frontend-lead, ui-designer, growth-agent]
tags: [landing-page, conversion, design]
contract:
  prerequisites:
    - "the offer, audience, and message spine"
  preferred_agents: [frontend-lead, ui-designer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "design decisions tied to conversion intent"
  artifact_contract:
    - "landing page (structure, copy, states, verification)"
  quality_gates:
    - "value statement above the fold in audience language"
    - "one primary CTA"
    - "proof elements present (or a deliberate gap)"
    - "loading/error/empty states for dynamic sections"
    - "responsive + accessibility verified"
  verification:
    - "load in browser; check states and console"
  failure_modes:
    cluttered: "cut to one goal per viewport"
    trust_gap: "add proof or state the gap"
  escalation:
    - "offers with no proof available (escalate the gap)"
  handoff_in:
    - "offer, audience, message spine"
  handoff_out:
    - "landing page with verification evidence"
  evaluation:
    - "conversion-intent alignment"
    - "verification results"
  observability:
    - "record the page and its checks"
  related_skills: [copywriting, ui-design, frontend-engineering, seo]
---

# Landing Page Design

## Purpose
Design landing pages that convert: value above the fold, one CTA, proof,
complete states — verified in the browser.

## When to use / When NOT to use
- use: paid/SEO landing pages, product launches
- avoid: without the offer and message spine; avoid adding sections that
  dilute the single goal

## Inputs & assumptions
- inputs: offer, audience, message spine
- assumptions: traffic source and conversion goal assumed unless stated

## Workflow
1. State the single conversion goal and the primary CTA.
2. Structure: value promise → proof → mechanism → CTA, in the audience's
   language.
3. Write copy from the message spine (see copywriting).
4. Design all states (loading, empty, error) for dynamic sections.
5. Build responsive + accessible (see accessibility).
6. Verify in browser: load, states, console, CTA path.

## Evidence requirements
- Design decisions tied to conversion intent; verification evidence
  recorded.

## Artifact contract
- `landing-page`: structure, copy, states, CTA path, verification notes.

## Quality gates (definition of done)
- [ ] Value above the fold in audience language
- [ ] One primary CTA
- [ ] Proof present or the gap stated
- [ ] States covered
- [ ] Responsive + accessibility verified in browser

## Verification
- Load in browser; check states, console, and the CTA path end-to-end.

## Failure & recovery
| failure | recovery |
|---|---|
| clutter | cut to one goal per viewport |
| trust gap | add proof or state the gap |
| broken CTA path | fix and re-verify |

## Escalation
- Offers with no proof available — escalate the gap.

## Handoff
- receives: offer, audience, message spine
- passes: landing page with verification evidence

## Evaluation
The org evaluates this skill by conversion-intent alignment and
verification results.

## Observability
- Record the page structure and checks in the audit trail.

## References
- references/checklist.md — landing-page verification walkthrough