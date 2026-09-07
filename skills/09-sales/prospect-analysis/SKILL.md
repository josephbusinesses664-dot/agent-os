---
id: prospect-analysis
name: Prospect Analysis
description: "Prospect analysis — pains, triggers, authority, budget, timing — with known/inferred/unknown separation."
category: 09-sales
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: medium
cost_level: low
dependencies: [lead-research]
compatible_agents: [sales-analyst, lead-researcher]
tags: [prospects, analysis, qualification]
contract:
  prerequisites:
    - "a prospect and the offer being sold"
  preferred_agents: [sales-analyst, lead-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "pains and triggers evidenced, not assumed"
    - "known / inferred / unknown labels per attribute"
  artifact_contract:
    - "prospect analysis (pains, triggers, authority, budget, timing, angle)"
  quality_gates:
    - "never invent prospect information"
    - "each pain mapped to an offer angle or marked unmatched"
    - "qualification: BANT-ish labels with evidence"
  verification:
    - "re-check cited signals resolve"
  failure_modes:
    fabrication: "mark unknown — never invent"
    overreach: "one signal is not a pattern"
  escalation:
    - "high-value prospects with unclear authority"
  handoff_in:
    - "prospect"
    - "offer"
  handoff_out:
    - "prospect analysis with angle for outreach"
  evaluation:
    - "evidence-based qualification"
    - "zero fabrication"
  observability:
    - "record evidence per attribute"
  related_skills: [lead-research, outreach-drafting, sales-strategy]
---

# Prospect Analysis

## Purpose
Analyze a prospect to find the angle: pains, triggers, authority, budget,
timing — separating known, inferred, and unknown, and mapping pains to
offer angles.

## When to use / When NOT to use
- use: before outreach, before a call
- avoid: inventing prospect facts; avoid pattern-overreach from a single
  signal

## Inputs & assumptions
- inputs: prospect, offer
- assumptions: every inference labeled; the analysis inherits the
  assumption labels

## Workflow
1. Gather public evidence: role, company situation, pains (jobs, press,
   community), recent triggers (hiring, funding, launches).
2. Label each attribute known / inferred / unknown.
3. Assess qualification: pain, authority, budget, timing — with evidence
   per factor.
4. Map each pain to an offer angle; mark unmatched pains.
5. Produce the analysis with a recommended angle.

## Evidence requirements
- Pains/triggers evidenced; unknown marked unknown.

## Artifact contract
- `prospect-analysis`: attributes (known/inferred/unknown), qualification
  (pain, authority, budget, timing), pain→angle map, recommended angle.

## Quality gates (definition of done)
- [ ] Never invent prospect information
- [ ] Every pain mapped to an angle or marked unmatched
- [ ] Qualification labels evidence-backed
- [ ] Single-signal overreach avoided

## Verification
- Re-check cited signals resolve.

## Failure & recovery
| failure | recovery |
|---|---|
| missing info | mark unknown |
| overreach | gather more evidence or label the narrowness |
| unclear authority | note it; escalate if high value |

## Escalation
- High-value prospects with unclear authority — escalate the research need.

## Handoff
- receives: prospect, offer
- passes: prospect analysis with angle to outreach

## Evaluation
The org evaluates this skill by evidence-based qualification and zero
fabrication.

## Observability
- Record evidence per attribute in the audit trail.

## References
- references/patterns.md — trigger catalogs and qualification scoring