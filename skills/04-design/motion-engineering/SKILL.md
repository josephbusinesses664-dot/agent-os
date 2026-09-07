---
id: motion-engineering
name: Motion Engineering
description: "Purpose-driven motion — communicates hierarchy/state or is absent — with performance and reduced-motion discipline."
category: 04-design
version: 1.1.0
source: agent-os core library (GSAP methodology + performance discipline)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot, browser.evaluate]
risk_level: low
cost_level: low
dependencies: [gsap, ui-design]
compatible_agents: [motion-engineer, frontend-lead, ui-designer]
tags: [motion, animation, performance]
contract:
  prerequisites:
    - "an interface and the intent motion must serve"
  preferred_agents: [motion-engineer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "each animation justified by what it communicates"
    - "performance measurements where motion is heavy"
  artifact_contract:
    - "motion spec (purpose, timing, easing, reduced-motion behavior)"
  quality_gates:
    - "motion communicates state/hierarchy or is removed"
    - "prefers-reduced-motion respected"
    - "animations run at 60fps on target hardware"
    - "no motion on critical-path content load"
  verification:
    - "measure frames (browser.evaluate); toggle reduced motion"
  failure_modes:
    decoration_motion: "remove or re-purpose; motion must earn its cost"
    jank: "switch to transform/opacity only; reduce GPU load"
  escalation:
    - "motion requirements exceeding mobile performance budgets"
  handoff_in:
    - "interface"
    - "intent"
  handoff_out:
    - "motion spec to frontend implementation"
  evaluation:
    - "motion purposefulness"
    - "performance verification results"
  observability:
    - "record measured FPS and reduced-motion behavior"
  related_skills: [gsap, ui-design, accessibility, performance-review]
---

# Motion Engineering

## Purpose
Engineer motion that communicates hierarchy and state — or is absent.
Motion must earn its cost: purpose, performance, and reduced-motion
discipline are requirements, not afterthoughts.

## When to use / When NOT to use
- use: when motion serves a user goal (orientation, state change, hierarchy)
- avoid: decoration-only animation; avoid heavy motion on content-critical
  paths; avoid motion that fights reduced-motion preferences

## Inputs & assumptions
- inputs: interface, intent
- assumptions: target hardware tier assumed unless stated (mobile mid-range
  is the floor)

## Workflow
1. For each candidate animation, state what it communicates (state change,
   hierarchy, causality). If nothing: cut it.
2. Design timing/easing from a motion language, not per-element whims.
3. Implement with transform/opacity (GPU-friendly) and cleanup on unmount.
4. Measure: FPS on target hardware; fix jank by simplifying.
5. Add reduced-motion handling: `prefers-reduced-motion` replaces motion
   with instant state change.
6. Verify: frames measured, reduced-motion toggled, no motion on critical
   load.

## Evidence requirements
- Every animation justified by communication purpose.
- Performance claims backed by measurements (browser.evaluate).

## Artifact contract
- `motion-spec`: per-animation purpose, timing, easing, triggers,
  reduced-motion behavior, measured FPS.

## Quality gates (definition of done)
- [ ] Motion communicates state/hierarchy or is removed
- [ ] Reduced-motion respected
- [ ] 60fps measured on target hardware
- [ ] No motion on critical-path content load
- [ ] Cleanup verified (no leaks on unmount/route change)

## Verification
- Measure FPS during animations in a real browser.
- Toggle reduced motion and confirm instant-state behavior.

## Failure & recovery
| failure | recovery |
|---|---|
| decoration motion | cut it or re-purpose |
| jank | transform/opacity only; lower GPU cost; simplify |
| leak on unmount | kill tweens/observers in cleanup; retest |

## Escalation
- Motion requirements exceeding mobile performance budgets — escalate the
  trade (simplify or accept lower tier).

## Handoff
- receives: interface, intent
- passes: motion spec to frontend implementation

## Evaluation
The org evaluates this skill by motion purposefulness and measured
performance — a beautiful animation that janks fails.

## Observability
- Record measured FPS, reduced-motion behavior, and cleanup verification.

## References
- references/patterns.md — timing systems and GPU-cost rules