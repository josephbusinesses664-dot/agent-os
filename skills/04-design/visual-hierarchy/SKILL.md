---
id: visual-hierarchy
name: Visual Hierarchy
description: "Visual hierarchy as engineering — focal points, grouping, weight, flow — with verification against intent."
category: 04-design
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [ui-design, design-quality]
compatible_agents: [ui-designer, frontend-lead]
tags: [hierarchy, visual-design]
contract:
  prerequisites:
    - "interface and the intent it must communicate"
  preferred_agents: [ui-designer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "hierarchy claims verified against the rendered interface"
  artifact_contract:
    - "hierarchy review (focal points, weight, flow, findings)"
  quality_gates:
    - "one clear focal point per view"
    - "visual weight matches information importance"
    - "reading flow matches task order"
  verification:
    - "screenshot and scan order: does the eye land where the task requires?"
  failure_modes:
    everything_important: "force a single focal point"
    contrast_by_color_only: "add weight/size cues — color alone fails"
  escalation:
    - "hierarchy conflicts with brand requirements"
  handoff_in:
    - "interface"
    - "intent"
  handoff_out:
    - "hierarchy review with findings and fixes"
  evaluation:
    - "focal-point clarity"
    - "weight-information alignment"
  observability:
    - "record the hierarchy review outcome"
  related_skills: [ui-design, design-quality, typography]
---

# Visual Hierarchy

## Purpose
Engineer hierarchy deliberately: one focal point per view, visual weight
matched to information importance, and a reading flow that matches the task
order.

## When to use / When NOT to use
- use: any screen where users must act or decide
- avoid: reviewing hierarchy without knowing the intent (the focal point
  depends on the task)

## Inputs & assumptions
- inputs: interface, intent (what the user must do/decide)
- assumptions: the primary task per view is assumed unless stated

## Workflow
1. State the primary task per view.
2. Identify the focal point: does the eye land on the primary action/data?
3. Check weight alignment: size, contrast, and spacing follow information
   importance — not decoration.
4. Check the reading flow: does scan order match task order?
5. Check redundancy: hierarchy must survive color-only (add weight/size
   cues).
6. Produce findings with fixes.

## Evidence requirements
- Hierarchy claims verified against the rendered interface — an opinion
  without a screenshot inspection is not a finding.

## Artifact contract
- `hierarchy-review`: per-view focal point, weight audit, flow audit,
  findings with fixes.

## Quality gates (definition of done)
- [ ] One focal point per view
- [ ] Weight matches importance
- [ ] Flow matches task order
- [ ] Hierarchy survives color-only removal

## Verification
- Screenshot each view; trace the scan order with the task in mind.

## Failure & recovery
| failure | recovery |
|---|---|
| everything emphasized | force one focal point |
| color-only differentiation | add weight/size cues |
| flow mismatch | reorder/regroup elements to match the task |

## Escalation
- Hierarchy conflicting with hard brand requirements — escalate the trade.

## Handoff
- receives: interface, intent
- passes: hierarchy review with fixes

## Evaluation
The org evaluates this skill by focal-point clarity and
weight-information alignment.

## Observability
- Record the review outcome in the project.

## References
- references/checklist.md — focal-point and weight audit steps