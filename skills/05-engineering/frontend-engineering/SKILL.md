---
id: frontend-engineering
name: Frontend Engineering
description: Production frontend engineering — React/Next/TS, components, state, API integration, performance, a11y, testing.
category: 05-engineering
version: 1.0.0
source: agent-os core library (Addy Osmani review methodology adapted)
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [frontend, react, engineering]
compatible_agents: [frontend-lead, ai-engineer]
---

# Frontend Engineering

## Purpose
Build polished, production-quality frontends where design quality is an
explicit engineering requirement — not an afterthought.

## Standards
1. **TypeScript everywhere** — strict mode; typed props/state/API responses;
   no `any` leaks at boundaries.
2. **Component architecture** — small focused components; props are the
   contract; composition over prop-drilling; one job per component.
3. **State management** — local state by default; server cache (React Query) for
   async; global store only for true cross-cutting state. No store-by-default.
4. **API integration** — typed client, error handling on every call, loading +
   error + empty states rendered, optimistic updates where UX benefits.
5. **Styling** — token-based (design tokens), responsive by default, no magic
   pixels; Tailwind or CSS modules per project convention.
6. **Performance** — code-split routes, lazy-load heavy deps, memoize
   selectively (profile first), avoid layout thrash, images sized/optimized.
7. **Accessibility** — semantic HTML, keyboard operable, visible focus,
   labeled inputs, reduced-motion respected.
8. **Testing** — unit tests for logic, component tests for behavior, e2e for
   critical paths. Tests must actually run.

## Definition of done
- Typecheck passes; lint passes; tests pass (evidence).
- All states implemented; a11y pass; performance budget met.