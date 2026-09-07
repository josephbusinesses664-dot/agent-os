---
id: performance-review
name: Performance Review
description: Review performance — runtime, load, frontend budgets, database queries.
category: 06-testing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read]
risk_level: low
cost_level: low
tags: [performance, review]
compatible_agents: [performance-reviewer, qa-director]
---

# Performance Review

## Purpose
Find performance problems before users do — with measurements, not guesses.

## Checklist
1. **Frontend** — LCP < 2.5s, CLS < 0.1, INP < 200ms (real device/network);
   bundle size sanity; images sized; no render-blocking junk; animation
   budgets (transform/opacity only).
2. **Backend** — hot paths: N+1 queries, missing indexes, sync I/O in async
   loops, unbounded caches, no timeouts on external calls.
3. **Data** — query plans on hot queries; pagination enforced; bulk
   operations batched.
4. **Concurrency** — locking, contention, connection pool sizes.
5. **Scale test** — the critical path under 10× normal load: latency, error
   rate, saturation points.

## Finding format
```
severity: critical | high | medium | low
location: <where>
problem: <the inefficiency>
evidence: <measurement or profile trace>
fix: <concrete change>
```

## Rules
- Every performance claim needs a measurement (profile, trace, load test).
- Optimize measured problems only; flag speculation separately.