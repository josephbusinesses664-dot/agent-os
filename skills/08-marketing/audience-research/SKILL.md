---
id: audience-research
name: Audience Research
description: "Evidence-based audience research — segments, pains, language, channels — with labeled inference."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [market-research, community-intelligence]
compatible_agents: [market-researcher, growth-agent, content-agent]
tags: [audience, research, segments]
contract:
  prerequisites:
    - "the product and the decision audience research informs"
  preferred_agents: [market-researcher, growth-agent]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "segment claims backed by sources"
    - "known / inferred / unknown separation per segment"
  artifact_contract:
    - "audience research (segments, pains, language, channels)"
  quality_gates:
    - "segments distinguishable and reachable"
    - "every pain labeled known / inferred / unknown"
  verification:
    - "check segment evidence diversity (not one source)"
  failure_modes:
    stereotype: "label inference; find evidence or mark unknown"
    overreach: "one community ≠ the whole segment"
  escalation:
    - "product-market mismatch signals"
  handoff_in:
    - "product"
    - "research decision"
  handoff_out:
    - "audience segments with evidence and channels"
  evaluation:
    - "evidence-backed segments"
    - "honest known/inferred/unknown labeling"
  observability:
    - "record sources per segment"
  related_skills: [market-research, messaging, community-intelligence]
---

# Audience Research

## Purpose
Segment the audience on evidence: who has the pain, how they talk about it,
where they gather — separating known from inferred from unknown.

## When to use / When NOT to use
- use: before messaging, positioning, channel decisions
- avoid: inventing personas from stereotypes; avoid building messaging on
  segments with no evidence

## Inputs & assumptions
- inputs: product, research decision
- assumptions: every inference labeled; a segment built on an assumption
  inherits it

## Workflow
1. State the decision this research informs (channels? messaging?
   positioning?).
2. Find where the audience gathers and complains (communities, reviews,
   forums, job posts).
3. Cluster by pain, behavior, and language — not demographics alone.
4. For each segment: pains (known/inferred/unknown), vocabulary (verbatim),
   channels, buying behavior signals.
5. Rank segments by fit with the product.
6. Produce the research with sources.

## Evidence requirements
- Segment claims backed by sources with retrieval dates.
- Known / inferred / unknown separation per segment — never present an
  inference as a fact.

## Artifact contract
- `audience-research`: segments (pains, language, channels, evidence),
  confidence per segment, unknowns.

## Quality gates (definition of done)
- [ ] Segments distinguishable and reachable
- [ ] Every pain labeled known / inferred / unknown
- [ ] Evidence diversity (≥2 independent sources per load-bearing claim)
- [ ] Vocabulary preserved verbatim

## Verification
- Check segment evidence diversity; re-check cited sources resolve.

## Failure & recovery
| failure | recovery |
|---|---|
| stereotype segments | find evidence or mark unknown |
| single-source overreach | label the narrowness explicitly |
| no buying signals | say so — do not invent demand |

## Escalation
- Product-market mismatch signals — escalate with the evidence.

## Handoff
- receives: product, research decision
- passes: audience segments with evidence and channels to messaging/
  positioning

## Evaluation
The org evaluates this skill by evidence-backed segments and honest
known/inferred/unknown labeling.

## Observability
- Record sources per segment in the audit trail.

## References
- references/patterns.md — segment clustering and evidence rules