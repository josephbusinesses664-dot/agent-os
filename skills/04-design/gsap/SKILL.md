---
id: gsap
name: GSAP Animation
description: "GSAP engineering — timelines, ScrollTrigger, performance, cleanup, reduced motion — as an executable operating procedure."
category: 04-design
version: 1.1.0
source: agent-os core library (GSAP methodology + performance discipline)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot, browser.evaluate, repo.search]
risk_level: low
cost_level: medium
dependencies: [motion-engineering]
compatible_agents: [motion-engineer, frontend-lead]
tags: [gsap, animation, scrolltrigger, timeline]
contract:
  prerequisites:
    - "a defined motion purpose (see motion-engineering)"
    - "access to the codebase where animation is implemented"
  preferred_agents: [motion-engineer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "performance measured, not assumed"
    - "cleanup verified on unmount/route change"
  artifact_contract:
    - "GSAP implementation (timelines, triggers, cleanup, reduced-motion)"
  quality_gates:
    - "animations use transform/opacity"
    - "tweens killed on cleanup; ScrollTrigger.revert() called"
    - "prefers-reduced-motion respected"
    - "60fps measured where ScrollTrigger pins/scrubs"
  verification:
    - "browser.evaluate: check cleanup state, measure frame rate"
  failure_modes:
    leak: "kill tweens and revert ScrollTriggers in cleanup"
    scroll_jank: "reduce pinned elements, use scrub with restraint"
  escalation:
    - "motion exceeding mobile budgets (escalate the simplification trade)"
  handoff_in:
    - "motion spec"
    - "codebase"
  handoff_out:
    - "GSAP implementation + measured performance notes"
  evaluation:
    - "correct GSAP API usage"
    - "cleanup and reduced-motion correctness"
    - "measured performance"
  observability:
    - "record measured FPS and cleanup verification"
  related_skills: [motion-engineering, frontend-engineering, performance-review, gsap-scrolltrigger]
---

# GSAP Animation

## Purpose
Implement GSAP animations as engineered features: correct API usage,
transform-only motion, reliable cleanup, ScrollTrigger discipline, and
reduced-motion support — verified in a real browser.

## When to use / When NOT to use
- use: when the motion spec calls for timeline/scroll-driven animation
- avoid: for motion better done in CSS (simple hovers/transitions); avoid
  ScrollTrigger pinning that buys nothing

## Inputs & assumptions
- inputs: motion spec, codebase
- assumptions: GSAP is registered per the project's bundler; assume the
  plugin set needed (ScrollTrigger, etc.) is declared

## Workflow
1. Read the motion spec: purpose, timing, triggers.
2. Implement with transform/opacity only; avoid layout-animating properties.
3. Use timelines for sequencing (gsap.timeline with position parameters).
4. ScrollTrigger: pin/scrub only where it communicates; revert everything.
5. Cleanup: kill tweens, revert triggers, remove observers on unmount/route
   change — for every framework lifecycle.
6. Reduced motion: gate heavy animation behind prefers-reduced-motion.
7. Verify in browser: frames, cleanup state, reduced-motion behavior.

## Evidence requirements
- Performance measured with browser.evaluate (frame times during
  animation).
- Cleanup verified: no active tweens after unmount.

## Artifact contract
- `gsap-implementation`: timelines, triggers, cleanup code, reduced-motion
  handling, measured FPS notes.

## Quality gates (definition of done)
- [ ] Transform/opacity only
- [ ] All tweens killed + ScrollTrigger.revert() on cleanup
- [ ] prefers-reduced-motion respected
- [ ] 60fps measured where ScrollTrigger pins/scrubs

## Verification
- browser.evaluate: confirm no lingering tweens after navigation.
- Measure FPS during the animation on the target viewport.

## Failure & recovery
| failure | recovery |
|---|---|
| memory leak | kill tweens/revert triggers in cleanup; retest |
| scroll jank | cut pinned elements; soften scrub; simplify |
| reduced-motion ignored | gate the animation; verify toggle |

## Escalation
- Motion exceeding mobile budgets — escalate the simplification trade.

## Handoff
- receives: motion spec, codebase
- passes: GSAP implementation with measured performance notes

## Evaluation
The org evaluates this skill by correct GSAP usage, cleanup correctness,
reduced-motion handling, and measured performance.

## Observability
- Record measured FPS and cleanup verification in the audit trail.

## References
- references/patterns.md — timeline patterns and ScrollTrigger recipes