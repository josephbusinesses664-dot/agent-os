---
id: accessibility
name: Accessibility
description: WCAG-oriented accessibility for web UI — semantics, contrast, keyboard, focus, reduced motion.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [accessibility, a11y, wcag]
compatible_agents: [ux-designer, ui-designer, frontend-lead, test-engineer]
---

# Accessibility

## Purpose
Make interfaces usable by everyone: screen readers, keyboard-only, low vision,
motor impairments, vestibular sensitivity. Accessibility is a requirement, not
a feature.

## Checklist
1. **Semantics** — real elements (`<button>`, `<nav>`, `<h1>…`), not divs with
   click handlers; one `<h1>` per page; logical heading order.
2. **Contrast** — text ≥ 4.5:1 (large text ≥ 3:1); non-text UI ≥ 3:1.
3. **Keyboard** — every action reachable and operable via keyboard; visible
   focus indicator; logical tab order; no keyboard traps.
4. **Labels** — every input labeled; icon buttons have accessible names.
5. **Reduced motion** — honor `prefers-reduced-motion`: no auto-playing loops,
   no large parallax; keep essential state changes instant.
6. **Screen reader** — aria-live for dynamic updates; alt text for meaningful
   images; aria-hidden for decoration.
7. **Target size** — ≥ 44x44px for touch targets.
8. **Errors** — errors identified in text and programmatically (role=alert,
   aria-describedby).

## Verification
- Keyboard-only pass of every flow.
- Automated checks (axe-style) clean; manual review of dynamic regions.
- Zoom to 200%: no content loss or overlap.