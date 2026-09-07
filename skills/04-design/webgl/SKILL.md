---
id: webgl
name: WebGL / Shaders
description: "WebGL and shader engineering — GPU cost, shader complexity, DPR, cleanup — used only where it improves the product."
category: 04-design
version: 1.1.0
source: agent-os core library (Three.js/WebGL methodology + performance discipline)
license: MIT
capability_type: skill
required_tools: [browser.open, browser.evaluate, repo.search]
risk_level: low
cost_level: high
dependencies: [threejs, performance-review]
compatible_agents: [motion-engineer, frontend-lead]
tags: [webgl, shaders, gpu]
contract:
  prerequisites:
    - "a purpose that genuinely requires custom GPU work"
    - "performance budget and target hardware"
  preferred_agents: [motion-engineer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: high
  expected_latency: hours
  evidence_requirements:
    - "shader cost measured (fragment complexity, FPS) on target tier"
  artifact_contract:
    - "WebGL implementation (shaders, uniforms, budgets, cleanup)"
  quality_gates:
    - "custom shaders justified over built-in materials"
    - "texture sizes and DPR capped"
    - "no per-frame uniform allocation"
    - "context lost/restore handled; resources disposed on cleanup"
    - "reduced-motion fallback"
  verification:
    - "measure FPS and memory on target tier"
  failure_modes:
    shader_bloat: "reduce fragment cost; simplify or precompute"
    context_loss: "handle restore or degrade gracefully"
  escalation:
    - "GPU work exceeding budget (escalate cut vs optimize)"
  handoff_in:
    - "purpose"
    - "budget"
  handoff_out:
    - "WebGL implementation + measured cost"
  evaluation:
    - "shader-cost awareness"
    - "measured performance"
  observability:
    - "record FPS, texture budgets, context-loss handling"
  related_skills: [threejs, motion-engineering, performance-review]
---

# WebGL / Shaders

## Purpose
Engineer custom GPU work (shaders, post-processing) that stays inside a
cost budget and handles the GPU's failure modes — used only where it
genuinely improves the product.

## When to use / When NOT to use
- use: effects impossible with standard materials (custom deformation,
  data-driven visuals, post-processing with real purpose)
- avoid: when a built-in material, CSS, or GSAP achieves the effect —
  custom shaders are the most expensive tool in the stack

## Inputs & assumptions
- inputs: purpose, performance budget
- assumptions: target hardware tier assumed; mobile mid-range is the floor

## Workflow
1. Justify custom GPU work; prefer built-ins where sufficient.
2. Budget: texture sizes, DPR cap, uniform counts, draw calls.
3. Write shaders with fragment-cost discipline (branching, overdraw,
   texture fetches).
4. Avoid per-frame allocations (uniforms, buffers) — reuse.
5. Handle context loss/restore and device downgrades.
6. Reduced motion: replace heavy GPU effects with a static frame.
7. Cleanup: dispose programs, buffers, textures; stop the loop.
8. Verify measured FPS/memory on the target tier.

## Evidence requirements
- Shader cost measured, not assumed.
- Justification for custom GPU work documented.

## Artifact contract
- `webgl-implementation`: shaders, uniform/buffer budget, DPR caps,
  context-loss handling, cleanup, measured cost.

## Quality gates (definition of done)
- [ ] Custom GPU work justified
- [ ] DPR/texture budgets capped
- [ ] No per-frame allocation
- [ ] Context loss handled
- [ ] Reduced-motion fallback present
- [ ] Measured FPS within budget

## Verification
- Measure FPS/memory on the target tier with browser.evaluate.

## Failure & recovery
| failure | recovery |
|---|---|
| shader bloat | reduce fragment cost; precompute; simplify |
| context loss | handle restore or degrade gracefully |
| mobile jank | quality-tier downgrade on low-end |

## Escalation
- GPU work exceeding the budget — escalate cut vs optimize.

## Handoff
- receives: purpose, budget
- passes: WebGL implementation + measured cost

## Evaluation
The org evaluates this skill by shader-cost awareness and measured
performance within budget.

## Observability
- Record FPS, texture/uniform budgets, and context-loss handling.

## References
- references/patterns.md — shader-cost rules and fallback tiers