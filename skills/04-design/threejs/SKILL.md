---
id: threejs
name: Three.js / WebGL
description: "Three.js engineering — GPU budgets, draw calls, DPR, cleanup, reduced-motion — knowing when NOT to use WebGL."
category: 04-design
version: 1.1.0
source: agent-os core library (Three.js/R3F methodology + performance discipline)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.evaluate, repo.search]
risk_level: low
cost_level: high
dependencies: [motion-engineering, performance-review]
compatible_agents: [motion-engineer, frontend-lead]
tags: [threejs, webgl, 3d, gpu]
contract:
  prerequisites:
    - "a motion/product purpose that genuinely needs 3D"
    - "target hardware tier and performance budget"
  preferred_agents: [motion-engineer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: high
  expected_latency: hours
  evidence_requirements:
    - "measured GPU cost (draw calls, FPS, memory) on target hardware"
  artifact_contract:
    - "Three.js implementation (scene, assets, budgets, cleanup, reduced-motion)"
  quality_gates:
    - "3D justified — WebGL used because it improves the product, not because it exists"
    - "draw calls and texture sizes within budget"
    - "DPR capped on mobile"
    - "renderer disposed and RAF loop stopped on cleanup"
    - "reduced-motion fallback present"
  verification:
    - "measure FPS and memory; test on mobile tier"
  failure_modes:
    gpu_bloat: "reduce draw calls, cap DPR, compress textures"
    mobile_jank: "downgrade quality tier on low-end devices"
  escalation:
    - "3D features that blow the performance budget (escalate cut vs optimize)"
  handoff_in:
    - "motion/product purpose"
    - "performance budget"
  handoff_out:
    - "Three.js implementation + measured performance"
  evaluation:
    - "GPU-cost awareness"
    - "measured performance within budget"
    - "cleanup correctness"
  observability:
    - "record draw calls, FPS, memory measurements"
  related_skills: [webgl, motion-engineering, gsap, performance-review, frontend-engineering]
---

# Three.js / WebGL

## Purpose
Engineer Three.js scenes that stay inside a performance budget: GPU cost is
a first-class constraint, cleanup is verified, and reduced-motion/quality
tiers exist. The first decision is whether 3D is needed at all.

## When to use / When NOT to use
- use: genuinely spatial/3D product value (product viewers, data
  visualization, immersive brand moments with budget)
- avoid: marketing decoration where CSS/GSAP achieves the effect at 1/100th
  the GPU cost; avoid WebGL for anything a 2D canvas or DOM can do

## Inputs & assumptions
- inputs: product purpose, performance budget, target hardware
- assumptions: budget and hardware tier assumed unless stated; mobile
  mid-range is the default floor

## Workflow
1. **Justify 3D** — state what only WebGL can deliver. If a cheaper medium
   suffices, recommend it.
2. **Budget** — set draw-call, texture-size, and DPR caps for the target
   tier.
3. **Assets** — compress models/textures; cap texture sizes; reuse
   geometries/materials.
4. **Render** — cap DPR (mobile ≤2), batch draw calls, avoid per-frame
   allocations.
5. **Cleanup** — dispose geometries/materials/textures; stop the RAF loop;
   remove resize observers.
6. **Tiers** — quality tiering: low-end devices get reduced geometry/effects.
7. **Reduced motion** — prefers-reduced-motion swaps 3D for a static/first
   frame.
8. **Verify** — measure FPS/memory on the target tier.

## Evidence requirements
- GPU cost measured (draw calls, FPS, memory), not assumed.
- 3D justification documented in the artifact.

## Artifact contract
- `threejs-implementation`: scene structure, asset budget, DPR/draw-call
  caps, cleanup code, quality tiers, measured performance.

## Quality gates (definition of done)
- [ ] 3D justified in the artifact
- [ ] Draw calls and texture sizes within budget
- [ ] DPR capped on mobile
- [ ] Renderer disposed, RAF stopped on cleanup
- [ ] Reduced-motion fallback present
- [ ] Measured FPS on target tier

## Verification
- browser.evaluate: measure FPS and memory during the scene.
- Test on a mobile-sized viewport with DPR capped.

## Failure & recovery
| failure | recovery |
|---|---|
| GPU bloat | reduce draw calls, cap DPR, compress textures |
| mobile jank | downgrade quality tier on low-end |
| cleanup leak | dispose everything; retest after navigation |

## Escalation
- 3D blowing the performance budget — escalate the cut-vs-optimize trade.

## Handoff
- receives: product purpose, performance budget
- passes: Three.js implementation + measured performance

## Evaluation
The org evaluates this skill by GPU-cost awareness, measured performance
within budget, and cleanup correctness.

## Observability
- Record draw calls, FPS, and memory measurements in the audit trail.

## References
- references/patterns.md — optimization recipes and budget defaults