---
id: motion-engineering
name: Motion Engineering
description: Motion that improves UX — GSAP, ScrollTrigger, Lenis, transitions. Performance/a11y/mobile-first judgment.
category: 04-design
version: 1.0.0
source: agent-os core library (GSAP methodology)
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [motion, gsap, animation, scroll]
compatible_agents: [motion-engineer, design-director, frontend-lead]
---

# Motion Engineering

## Purpose
Use motion to clarify state, guide attention and add craft — never to decorate.
Every animation must justify itself on performance, accessibility and mobile.

## Decision gate (before animating)
- **Does it clarify?** (state change, spatial relation, cause-effect) → yes
- **Does it add brand craft?** (signature, delightful detail) → maybe, sparingly
- **Is it just for wow?** → no. Kill it.
- **Does it hurt a11y or perf?** → no or provide reduced/disabled variant.

## Craft rules
- Duration 150-300ms (UI feedback); 400-800ms (narrative/scroll reveals).
- Easing: ease-out for entrances, ease-in-out for loops; avoid linear unless data.
- Animate `transform` and `opacity` only (compositor-friendly); never layout
  properties (width, top) for movement.
- Stagger > 0.05s feels deliberate; > 0.15s feels slow.
- Respect `prefers-reduced-motion`: disable or minimize motion.
- Pause/hide animation when off-screen (ScrollTrigger + scrub carefully);
  clean up listeners/tweens on teardown.
- Mobile: reduce parallax scale; no heavy scroll-jacking; test 60fps on a
  mid-range device.

## Stack notes
- GSAP: `gsap.to/fromTo`, timelines for sequences, ScrollTrigger for scroll
  scenes, Flip for layout morphs.
- Lenis: smooth scrolling — pair with ScrollTrigger via `lenis.on('scroll',
  ScrollTrigger.update)`.
- Three.js/R3F/WebGL: only for genuinely immersive moments; keep bundle and
  GPU budget explicit; provide DOM fallback.