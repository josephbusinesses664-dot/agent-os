---
id: gsap
name: GSAP Animation
description: GSAP core, timelines, ScrollTrigger, Flip, SplitText usage patterns with cleanup and performance.
category: 04-design
version: 1.0.0
source: GSAP official methodology
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [gsap, animation, scrolltrigger]
compatible_agents: [motion-engineer, frontend-lead]
---

# GSAP Animation

## Core API
- `gsap.to(el, {x, opacity, duration, ease})` — animate to values.
- `gsap.fromTo(el, {from}, {to})` — explicit start/end (preferred for reveals).
- `gsap.timeline()` — sequence: `tl.to(...).to(...)`; use position params for
  overlap: `tl.to(a, {…}, "<")` (start together) or `"-=0.2"` (overlap).
- Easing: `power2.out` for UI, `power3.out`/`expo.out` for reveals,
  `power1.inOut` for continuous loops. Avoid `ease: "none"` except scrubbed.
- `gsap.matchMedia()` — responsive + `prefers-reduced-motion` handling:
  ```js
  const mm = gsap.matchMedia();
  mm.add("(min-width: 768px) and (prefers-reduced-motion: no-preference)", () => {
    const tween = gsap.to(...);
    return () => tween.kill(); // cleanup on unmatch
  });
  ```

## ScrollTrigger
- Reveal: `ScrollTrigger.create({trigger, start: "top 80%", once: true})` or
  scrub with `gsap.to(el, {scrollTrigger: {trigger, scrub: true}, y: …})`.
- Pin only when it earns it (long-form narrative); pinning can break layout.
- `refresh()` after images/fonts load; use `invalidateOnRefresh` for scrubbed.
- Always `ScrollTrigger.getAll().forEach(t => t.kill())` on unmount.

## React (useGSAP)
```js
useGSAP(() => { const tween = gsap.to(ref.current, {...}); return () => tween.kill(); }, {scope: containerRef});
```

## Performance
- Animate transforms/opacity; batch with `will-change` sparingly.
- Kill tweens on unmount; avoid animating huge DOM forests.