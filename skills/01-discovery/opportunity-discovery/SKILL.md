---
id: opportunity-discovery
name: Opportunity Discovery
description: "Find and structure market opportunities from pain points, gaps and signals, with evidence lineage."
category: 01-discovery
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [community-intelligence]
compatible_agents: [product-researcher, market-researcher, community-researcher]
tags: [opportunity, discovery, gaps, pain-points]
contract:
  prerequisites:
    - "a market or niche of interest"
    - "an appetite for breadth over depth (this is discovery, not validation)"
  preferred_agents: [product-researcher, community-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "each opportunity backed by at least one concrete signal with source"
    - "pain points separated from feature requests from hype"
    - "customer language preserved verbatim where it matters"
  artifact_contract:
    - "opportunity list (candidate, signal, source, confidence)"
  quality_gates:
    - "no opportunity listed without a signal and source"
    - "opportunities ranked by signal strength, not excitement"
    - "loud-minority vs population-level distinction explicit"
  verification:
    - "spot-check that each cited signal exists at its source"
  failure_modes:
    no_signal: "report the niche as low-evidence rather than padding the list"
    shallow_source: "one subreddit alone is a loud minority — say so"
  escalation:
    - "an opportunity with strong signals but high build cost (hand off with both sides)"
  handoff_in:
    - "market or niche"
    - "search breadth constraints"
  handoff_out:
    - "opportunity candidates with signals and sources"
    - "confidence per candidate"
    - "recommended validation order"
  evaluation:
    - "every candidate has evidence"
    - "signal types correctly classified"
    - "ranking matches evidence strength"
  observability:
    - "log candidate → signal → source mapping"
  related_skills: [opportunity-scoring, demand-validation, community-intelligence, reddit-research]
---

# Opportunity Discovery

## Purpose
Generate a ranked list of market opportunities from pain points, product
gaps and demand signals — each with evidence lineage, so the organization can
decide what to validate next.

## When to use / When NOT to use
- use: at the start of a project, when hunting for the next idea, when asked
  "what should we build"
- avoid: when an idea already exists and needs validation (use
  demand-validation); avoid when the question is "how big is it" (use
  market-sizing)

## Inputs & assumptions
- inputs: market/niche, breadth constraints
- assumptions: the niche definition itself is a hypothesis — record it

## Workflow
1. Frame the niche and the search surface (communities, forums, job posts,
   review sites, adjacent tools).
2. Collect signals: complaints, workarounds, feature requests, replacement
   intent, purchase intent, buying-intent language.
3. For each signal record source + date + verbatim excerpt (customer
   language preserved).
4. Cluster into candidate opportunities; note recurrence across independent
   sources.
5. Distinguish loud minority (high engagement, narrow population) from
   population-level problem (recurring across diverse sources).
6. Rank candidates by signal strength and breadth; add the weakest at the
   bottom with a low-confidence label.
7. Hand off the top candidates to scoring/validation with a recommended order.

## Evidence requirements
- Every candidate opportunity must have ≥1 concrete signal with source.
- If a niche has no signals, report it as low-evidence — do not pad the list
  with plausible-sounding "opportunities".

## Artifact contract
- `opportunity-list`: candidate, signal inventory (source, date, excerpt),
  signal type, confidence, recommended validation order.

## Quality gates (definition of done)
- [ ] Every opportunity has a signal and source
- [ ] Ranking reflects evidence strength
- [ ] Loud-minority vs population-level distinction explicit
- [ ] Customer language preserved (quotes, not paraphrases) where it matters

## Verification
- Spot-check the top 3 candidates' signals resolve at their sources.
- Re-read the list for opportunities that only restate the niche with no
  added evidence — remove them.

## Failure & recovery
| failure | recovery |
|---|---|
| no signals found | widen surface, then report low-evidence niche honestly |
| single-source signals | label narrow, mark low confidence, seek corroboration |
| signal overload | cluster and deduplicate, rank, keep only the strongest evidence per cluster |

## Escalation
- High-signal, high-build-cost opportunities — escalate with both the signal
  evidence and the build-cost sketch for an explicit decision.

## Handoff
- receives: market/niche, breadth constraints
- passes: candidates with signals+sources, confidence per candidate,
  recommended validation order

## Evaluation
The org evaluates this skill by whether every candidate carries evidence,
signal types are classified correctly, and ranking matches evidence strength
rather than narrative appeal.

## Observability
- Trace candidate → signal → source mappings and the final ranking order.

## References
- references/patterns.md — signal archetypes and cluster patterns