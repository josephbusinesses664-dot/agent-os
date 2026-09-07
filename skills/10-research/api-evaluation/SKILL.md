---
id: api-evaluation
name: API Evaluation
description: "Evidence-based API selection — cost, limits, auth, reliability, commercial use — with verification."
category: 10-research
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [technical-research]
compatible_agents: [technical-researcher, ai-engineer, backend-lead]
tags: [api, evaluation, integration]
contract:
  prerequisites:
    - "the capability needed and the decision it serves"
  preferred_agents: [technical-researcher, backend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "pricing/limits verified against current provider pages"
    - "commercial-use restrictions checked"
  artifact_contract:
    - "api evaluation (options, criteria, verdict, verification)"
  quality_gates:
    - "options compared on explicit criteria"
    - "pricing current and sourced"
    - "free/low-cost preferred when sufficient"
    - "verdict matches the evidence"
  verification:
    - "re-check pricing pages and docs"
  failure_modes:
    stale_pricing: "re-verify against current pages"
    hidden_restrictions: "check commercial use and rate limits explicitly"
  escalation:
    - "no API meeting the requirements within budget"
  handoff_in:
    - "capability needed"
  handoff_out:
    - "api evaluation with verdict"
  evaluation:
    - "criteria coverage"
    - "evidence freshness"
  observability:
    - "record options and sources"
  related_skills: [technical-research, api-integration, tech-decision]
---

# API Evaluation

## Purpose
Choose APIs on evidence: compare options against explicit criteria —
availability, cost, auth, rate limits, reliability, commercial use — with
current, sourced pricing.

## When to use / When NOT to use
- use: selecting an API/service for integration
- avoid: recommending from memory — pricing and limits change; avoid
  ignoring commercial-use restrictions

## Inputs & assumptions
- inputs: capability needed
- assumptions: usage volume assumed unless stated — cost conclusions
  depend on it

## Workflow
1. State the capability and the criteria that matter.
2. Gather candidates; for each: pricing (current, sourced), rate limits,
   auth requirements, reliability signals, commercial-use terms.
3. Score against criteria; prefer free/low-cost when sufficient.
4. Verify the top options against current pages.
5. Produce the verdict with the evidence.

## Evidence requirements
- Pricing/limits verified against current provider pages with dates.
- Commercial-use restrictions explicitly checked.

## Artifact contract
- `api-evaluation`: options (criteria scores, evidence), verdict,
  verification notes.

## Quality gates (definition of done)
- [ ] Options compared on explicit criteria
- [ ] Pricing current and sourced
- [ ] Commercial use checked
- [ ] Free/low-cost preferred when sufficient

## Verification
- Re-check pricing pages and docs for the top options.

## Failure & recovery
| failure | recovery |
|---|---|
| stale pricing | re-verify current pages |
| hidden restrictions | check terms explicitly |
| no fit in budget | escalate with the gap |

## Escalation
- No API meeting requirements within budget.

## Handoff
- receives: capability needed
- passes: api evaluation with verdict to integration

## Evaluation
The org evaluates this skill by criteria coverage and evidence freshness.

## Observability
- Record options and sources in the audit trail.

## References
- references/patterns.md — evaluation criteria sets