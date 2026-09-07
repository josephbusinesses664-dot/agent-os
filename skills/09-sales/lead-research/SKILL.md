---
id: lead-research
name: Lead Research
description: "Evidence-based lead research — ICP fit, buying signals, contacts — with known/inferred/unknown separation."
category: 09-sales
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: medium
cost_level: low
dependencies: [prospect-analysis]
compatible_agents: [lead-researcher, sales-analyst]
tags: [leads, research, icp]
contract:
  prerequisites:
    - "the ICP definition"
    - "permission to research prospects"
  preferred_agents: [lead-researcher, sales-analyst]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "fit signals cited with sources"
    - "known / inferred / unknown labeled per lead"
  artifact_contract:
    - "lead profiles (fit, signals, contacts, evidence)"
  quality_gates:
    - "never invent prospect information"
    - "fit scored on evidence"
    - "privacy respected (no scraping of private data)"
  verification:
    - "re-check cited signals resolve"
  failure_modes:
    fabrication: "never invent a prospect fact — mark unknown"
    privacy_overreach: "public sources only"
  escalation:
    - "high-fit leads with compliance concerns"
  handoff_in:
    - "ICP"
    - "target list"
  handoff_out:
    - "qualified leads with evidence for outreach"
  evaluation:
    - "evidence-backed fit"
    - "zero fabrication"
  observability:
    - "record lead sources"
  related_skills: [prospect-analysis, outreach-drafting, sales-strategy]
---

# Lead Research

## Purpose
Research prospects against the ICP with evidence: fit signals, buying
signals, contacts — labeling known, inferred, and unknown — without ever
inventing information.

## When to use / When NOT to use
- use: building target lists, qualifying inbound leads
- avoid: fabricating prospect facts; avoid scraping private data

## Inputs & assumptions
- inputs: ICP definition, target list
- assumptions: ICP itself is a hypothesis — record it and its evidence

## Workflow
1. Restate the ICP: role, company size, pain, budget signals.
2. For each prospect, gather public evidence: role, company, tech stack,
   pains (jobs, press, community), growth signals.
3. Score fit per lead with evidence citations.
4. Label each attribute known / inferred / unknown.
5. Rank the list; hand off the top to outreach.

## Evidence requirements
- Fit signals cited; unknown marked unknown — fabrication is the cardinal
  sin of this skill.

## Artifact contract
- `lead-profiles`: per-lead fit score, signals (source), contacts,
  known/inferred/unknown labels.

## Quality gates (definition of done)
- [ ] Never invent prospect information
- [ ] Fit scored on evidence
- [ ] Public sources only
- [ ] Unknowns explicit

## Verification
- Re-check cited signals resolve at their sources.

## Failure & recovery
| failure | recovery |
|---|---|
| missing info | mark unknown; do not invent |
| privacy overreach | public sources only |
| stale data | prefer recent sources; label vintage |

## Escalation
- High-fit leads with compliance concerns (regulated industries).

## Handoff
- receives: ICP, target list
- passes: qualified leads with evidence to outreach

## Evaluation
The org evaluates this skill by evidence-backed fit and zero fabrication.

## Observability
- Record lead sources in the audit trail.

## References
- references/patterns.md — signal catalogs and fit scoring