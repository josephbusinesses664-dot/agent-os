---
id: backend-engineering
name: Backend Engineering
description: Backend engineering — API design, auth, data, caching, queues, events, resilience.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [backend, api, services]
compatible_agents: [backend-lead, ai-engineer]
---

# Backend Engineering

## Standards
1. **API design** — resource-oriented REST (or explicit RPC); consistent error
   shape `{error: {code, message, details}}`; versioning strategy decided up
   front; idempotency keys for mutations.
2. **AuthN/AuthZ** — authentication via established mechanism (sessions/JWT per
   project); authorization checked server-side on every endpoint; never trust
   the client; least-privilege scopes.
3. **Data layer** — migrations in code; indexes justified by query plans;
   transactions where invariants span writes; no N+1.
4. **Validation** — validate and normalize all input at the boundary (schema
   validation); reject unknown fields where it matters.
5. **Caching** — cache reads at the right layer (HTTP/query/object); invalidation
   strategy explicit; cache stamps/penetration handled.
6. **Queues & jobs** — background work via queues with retries + dead-letter;
   idempotent handlers; backpressure.
7. **Events** — event-driven decoupling where it reduces coupling; event
   schemas versioned; at-least-once assumed → handlers idempotent.
8. **Resilience** — timeouts + retries with backoff + circuit breakers on
   external calls; graceful degradation; structured logging with request ids.

## Definition of done
- Tests for handlers + core logic pass (evidence).
- Migrations apply cleanly; env config documented; secrets never logged.