---
id: threejs
name: Three.js / R3F
description: Three.js and React Three Fiber usage — when justified, performance budgets, fallbacks.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [threejs, r3f, webgl, 3d]
compatible_agents: [motion-engineer, frontend-lead]
---

# Three.js / React Three Fiber

## When justified
Use 3D/WebGL only when it materially serves the experience (product
visualization, interactive demos, signature hero). Ask: does the message
survive without it? If yes, prefer DOM/CSS/2D canvas.

## R3F patterns
- Declarative scene: `<Canvas><mesh><boxGeometry/><meshStandardMaterial/></mesh></Canvas>`.
- `useFrame((state, delta) => …)` for per-frame updates; avoid allocations in the loop.
- `useLoader`/`useGLTF` for assets; draco-compress large models.
- Dispose geometries/materials on unmount (`useEffect` cleanup or
  `useMemo` + `dispose()`).
- DPR clamp: `<Canvas dpr={[1, 1.75]}>`; pause rendering when tab hidden or
  scene off-screen.

## Performance budget
- Draw calls < 100 typical; instancing for repeated meshes; merged geometry.
- Keep shader complexity sane; test on integrated GPU + mobile.
- Lazy-load the 3D bundle (dynamic import) so the page shell renders first.
- Provide a graceful fallback (poster image / CSS scene) while loading and for
  users without WebGL (`WebGL.isWebGLAvailable()` check).

## Rules
- If the 3D is decorative, remove it or gate it behind reduced-motion.
- Real interactions beat auto-rotation: orbit/pointer control earns its cost.