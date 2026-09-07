---
id: api-integration
name: API Integration
description: Integrate third-party APIs — auth, rate limits, error handling, keys, testing.
category: 20-integrations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: medium
cost_level: low
tags: [api, integration, http]
compatible_agents: [ai-engineer, backend-lead]
---

# API Integration

## Purpose
Integrate external APIs safely and reliably — evaluated first (see
api-evaluation), then wired with resilience.

## Checklist
1. **Credentials** — keys in env/config, never code; scoped keys where the
   provider allows; rotation plan.
2. **Client** — typed request/response at the boundary; timeouts everywhere.
3. **Rate limits** — respect headers; retry with backoff on 429; queue bursts.
4. **Error handling** — map provider errors to typed failures; never let a
   provider exception take down a workflow — degrade or escalate.
5. **Retries** — idempotent retries with jitter; dead-letter after N attempts.
6. **Testing** — mock the boundary for unit tests; contract tests against a
   sandbox/staging env; record real responses in fixtures.
7. **Observability** — log request id, latency, status, cost; alert on error
   rate.
8. **Change** — API versions change: pin versions, monitor deprecation
   notices.

## Rules
- Never send secrets or PII to third parties you haven't vetted.
- Every external dependency is a failure domain: design for its outage.