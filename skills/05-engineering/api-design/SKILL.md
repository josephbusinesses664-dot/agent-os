---
id: api-design
name: API Design
description: Design clean APIs — resource modeling, errors, versioning, pagination, contracts.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [api, rest, contract]
compatible_agents: [software-architect, backend-lead, ai-engineer]
---

# API Design

## Principles
1. **Contract first** — define the schema/OpenAPI before implementation; it is
   the agreement between producer and consumers.
2. **Resource modeling** — nouns for resources, verbs via methods; sub-resources
   only for true ownership; avoid deep nesting.
3. **Naming** — plural nouns (`/users`), kebab/pascal consistent; query params
   for filtering (`?status=active&limit=25`); snake_case or camelCase — pick
   one and be consistent.
4. **Errors** — consistent envelope with machine-readable code, human message,
   and details; correct HTTP status codes; never leak stack traces.
5. **Pagination** — cursor-based for large lists; return `next_cursor`; sort
   keys stable.
6. **Versioning** — URL or header versioning decided once; deprecated versions
   have sunset dates.
7. **Idempotency** — `Idempotency-Key` for payments/mutations that can retry.
8. **Security** — rate limits, auth on every endpoint, input validation,
   pagination caps, no sensitive data in logs.

## Agent compatibility
APIs consumed by agents need: clear docs, predictable JSON, generous rate
limits or documented costs — flag these in the API registry evaluation.