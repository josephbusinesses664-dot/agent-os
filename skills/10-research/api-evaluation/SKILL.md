---
id: api-evaluation
name: API Evaluation
description: Evaluate third-party APIs before integrating — availability, cost, auth, limits, reliability, agent fit.
category: 10-research
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
tags: [api, evaluation, integration]
compatible_agents: [technical-researcher, ai-engineer]
---

# API Evaluation

## Purpose
Choose APIs deliberately: an API that exists is not an API you should call.

## Rubric (score 0-5)
1. **Availability** — uptime, maturity, maintenance activity.
2. **Cost** — free tier adequacy; unit economics at real usage.
3. **Authentication** — complexity and security of the auth flow.
4. **Rate limits** — headroom for your actual load pattern.
5. **Documentation** — completeness, accuracy, current examples.
6. **Reliability** — error handling, SLAs, incident history.
7. **Commercial use** — license/ToS allow your business model.
8. **Data quality** — accuracy, coverage, update frequency.
9. **Security** — data handling, PII exposure, compliance.
10. **Agent compatibility** — predictable JSON, no fragile scraping.

## Process
1. Shortlist ≥ 3 candidates; read actual docs (not landing pages).
2. Score with evidence; flag dealbreakers (cost at scale, ToS, reliability).
3. Recommend one + fallback; document the exit path.
4. Register the choice in the API registry with the evaluation.

## Rules
- Prefer free/low-cost options when sufficient — don't pay for what you don't need.
- Never auto-call an API merely because it exists; every call must serve a task.