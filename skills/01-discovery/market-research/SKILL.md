---
id: market-research
name: Market Research
description: "Structured market research — segments, sizing inputs, competitors, demand validation, evidence with confidence."
category: 01-discovery
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [research-planning]
compatible_agents: [market-researcher, product-researcher, research-director]
tags: [market, research, segments, competitors]
contract:
  prerequisites:
    - "a defined market question and the decision it informs"
    - "a target segment or a hypothesis about one"
  preferred_agents: [market-researcher, product-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "multiple independent sources per claim where available"
    - "primary sources preferred (official docs, filings, pricing pages)"
    - "source diversity: not one aggregator dominating the conclusion"
  artifact_contract:
    - "market-research report (segments, competitors, evidence, confidence)"
  quality_gates:
    - "every estimate labeled observed / calculated / estimated / assumed"
    - "no fabricated citations or invented numbers"
    - "contradictions preserved, not resolved by assertion"
  verification:
    - "re-check source URLs and dates"
    - "cross-check key numbers against a second independent source"
  failure_modes:
    sparse_data: "say so, widen the source set, lower confidence"
    stale_data: "prefer recent sources, label vintage explicitly"
  escalation:
    - "key numbers that cannot be corroborated but drive the decision"
  handoff_in:
    - "research question"
    - "decision context"
  handoff_out:
    - "segments with evidence"
    - "competitor landscape"
    - "labeled estimates"
    - "unknowns"
  evaluation:
    - "source diversity and quality"
    - "correct labeling of observed vs estimated numbers"
    - "contradiction handling"
  observability:
    - "log sources with retrieval dates per claim"
  related_skills: [research-planning, evidence-synthesis, competitor-analysis, market-sizing]
---

# Market Research

## Purpose
Produce decision-grade market evidence: segments, size inputs, competitors —
with every number traceable to a source and every estimate labeled.

## When to use / When NOT to use
- use: entering a market, targeting a segment, sizing an opportunity
- avoid: validating one product idea (use demand-validation); deep dives into
  a single competitor (use competitor-analysis)

## Inputs & assumptions
- inputs: market question, decision context, segment hypothesis
- assumptions: label every assumption (TAM proxy, segment definition) as
  assumed — never present a proxy as a fact

## Workflow
1. **Decision first** — write the decision this research must inform; the
   report is complete when the decision has enough evidence, not when the
   search is exhausted.
2. **Question set** — decompose into segments, size inputs, competitive
   landscape, dynamics (growth, churn drivers).
3. **Query expansion** — for each question generate multiple query phrasings
   and source classes (official docs, filings, pricing pages, reputable
   journalism, community).
4. **Source ranking** — prefer primary sources; treat SEO aggregators as
   weak; require corroboration for load-bearing numbers.
5. **Extraction** — per claim record source, type, publication date,
   retrieval date, excerpt, confidence.
6. **Contradiction handling** — when sources disagree, preserve the
   contradiction and investigate why; never average to silence it.
7. **Synthesis** — organize by segment; label observed / calculated /
   estimated / assumed on every number.
8. **Report** — decision, evidence, confidence, unknowns, next step.

## Evidence requirements
- Claim-level provenance: source, source_type, publication_date,
  retrieval_date, excerpt, confidence, contradictory_evidence.
- If evidence is weak: say so, lower confidence, search more, or recommend
  an experiment. Never convert speculation into certainty.

## Artifact contract
- `market-research` report: decision, segments (with evidence), competitive
  landscape, labeled estimates, confidence, unknowns, next step.

## Quality gates (definition of done)
- [ ] Every estimate labeled observed / calculated / estimated / assumed
- [ ] Load-bearing numbers corroborated by a second independent source
- [ ] No fabricated citations
- [ ] Contradictions preserved with an investigation note
- [ ] Source diversity: no single source dominating conclusions

## Verification
- Re-check URLs resolve and dates are present.
- Cross-check the three most load-bearing numbers against independent
  sources; failures lower report confidence.

## Failure & recovery
| failure | recovery |
|---|---|
| sparse data | widen source set, lower confidence, escalate if decision-critical |
| stale data | prefer recent sources, label vintage explicitly |
| contradictory numbers | investigate both, preserve, escalate if decision-critical |

## Escalation
- Key numbers that cannot be corroborated but drive the decision.
- A segment decision where evidence is genuinely absent (escalate with the
  explicit unknown and a proposed experiment).

## Handoff
- receives: research question, decision context
- passes: segments with evidence, competitor landscape, labeled estimates,
  unknowns, recommended next research

## Evaluation
The org evaluates this skill by source diversity, correct labeling of
observed vs estimated numbers, and honest contradiction handling — not by
confidence of tone.

## Observability
- Record sources and retrieval dates per claim so a reviewer can replay the
  evidence trail.

## References
- references/methodology.md — source ranking and evidence extraction rules