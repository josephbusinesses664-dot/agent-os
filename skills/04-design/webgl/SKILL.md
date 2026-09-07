---
id: webgl
name: WebGL & Shaders
description: Shader-driven WebGL effects with disciplined budgets and fallbacks.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [webgl, shaders, effects]
compatible_agents: [motion-engineer, frontend-lead]
---

# WebGL & Shaders

## Purpose
Use GPU effects (gradients, distortion, particles, image effects) where they
create real impact — with explicit performance and fallback discipline.

## Rules
1. **Budget** — define target FPS (60 on desktop, 30+ on mobile). Measure with
   the performance panel; if it misses, simplify or drop.
2. **Resolution** — render at devicePixelRatio ≤ 2; consider half-res + upscale
   for full-screen effects.
3. **Uniforms over geometry** — animate uniforms, not thousands of vertices
   per frame; batch particles in one draw call.
4. **Pause off-screen** — stop the render loop when the element leaves the
   viewport or the tab is hidden.
5. **Reduced motion** — static/frozen fallback under `prefers-reduced-motion`.
6. **No WebGL fallback** — feature-detect and degrade to CSS effect or nothing;
   never a blank space.
7. **Bundle** — lazy-load the effect chunk; keep the critical path light.

## Quality signals
- No visible jank on scroll (test with ScrollTrigger scrubbing).
- Consistent framerate, no memory growth over time (watch for leaks).
- Effect enhances content; content remains readable and focused.