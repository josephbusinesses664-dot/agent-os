---
id: react-nextjs
name: React & Next.js
description: Current React/Next patterns — server components, data fetching, routing, forms, suspense.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [react, nextjs, app-router]
compatible_agents: [frontend-lead]
---

# React & Next.js

## Conventions
- **App Router** — routes as folders; `page.tsx`, `layout.tsx`, `loading.tsx`,
  `error.tsx`, `not-found.tsx` per route.
- **Server Components by default** — data fetching in RSC; `"use client"` only
  for interactivity; never fetch in a client component that could be a server one.
- **Data fetching** — `cache()`/`unstable_cache` for dedupe, `revalidateTag` for
  invalidation; loading/error boundaries for every data region.
- **Forms** — server actions with `useActionState` for pending states;
  progressive enhancement; validation on both sides.
- **Mutations** — revalidate/redirect after mutation; optimistic UI via
  transition APIs where latency matters.
- **Types** — typed routes (`typedRoutes`), typed search params; generate types
  from API schemas.

## Performance checklist
- `next/image` for images (sizes, priority only for LCP).
- Dynamic imports for client-heavy components; `Suspense` fallbacks.
- Watch bundle: no server-only code leaking into client chunks.
- Metadata API for SEO; viewport/themeColor set.

## Testing
- Vitest + Testing Library for components; Playwright for e2e on critical paths.
- Run against a real build (`next build`) — type errors, ESLint and build must pass.