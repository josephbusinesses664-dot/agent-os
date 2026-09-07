---
id: evidence-synthesis
name: Evidence Synthesis
description: "Evidence engineering — extraction, dedup, contradiction detection, confidence — claims ≠ facts."
category: 10-research
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [research-planning]
compatible_agents: [market-researcher, technical-researcher, community-researcher]
tags: [evidence, synthesis, research]
contract:
  prerequisites:
    - "research questions (from research-planning) and raw findings"
  preferred_agents: [market-researcher, technical-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "every claim carries source, date, excerpt, confidence"
    - "contradictions preserved, not averaged away"
  artifact_contract:
    - "evidence synthesis (claims, confidence, contradictions, conclusion)"
  quality_gates:
    - "claim ≠ fact — observation, inference, and assumption separated"
    - "deduplicated evidence"
    - "contradiction table present where sources disagree"
    - "confidence per conclusion"
  verification:
    - "spot-check cited sources; confirm excerpts match claims"
  failure_modes:
    false_certainty: "lower confidence — never inflate because the model sounds sure"
    source_dominance: "independent confirmation required for load-bearing claims"
  escalation:
    - "irreconcilable contradictions on decision-critical facts"
  handoff_in:
    - "research questions"
    - "raw findings"
  handoff_out:
    - "evidence synthesis with confidence and unknowns"
  evaluation:
    - "evidence quality (sources, dates)"
    - "contradiction handling"
    - "confidence calibration"
  observability:
    - "record claims with provenance"
  related_skills: [research-planning, market-research, competitor-analysis]
---

# Evidence Synthesis

## Purpose
Turn raw findings into decision-grade evidence: extract claims with
provenance, deduplicate, detect contradictions, and report confidence —
with the iron rule that claim ≠ fact.

## When to use / When NOT to use
- use: after gathering research findings, before drawing conclusions
- avoid: treating a confident-sounding summary as evidence; avoid averaging
  away contradictions

## Workflow
1. Extract claims: source, source_type, publication date, retrieval date,
   excerpt, confidence, relevance.
2. Deduplicate: same claim from many sources → one entry with source list.
3. Detect contradictions; build a contradiction table where sources
   disagree.
4. Separate observation / inference / assumption per claim.
5. Synthesize per question with a confidence level.
6. Report unknowns explicitly; recommend an experiment where evidence is
   thin.

## Evidence requirements
- Claims carry full provenance.
- Contradictions preserved and investigated, never silenced by averaging.

## Artifact contract
- `evidence-synthesis`: claims (with provenance), contradiction table,
  per-question conclusions with confidence, unknowns.

## Quality gates (definition of done)
- [ ] Claim ≠ fact separation (observation/inference/assumption)
- [ ] Deduplicated evidence
- [ ] Contradiction table present
- [ ] Confidence per conclusion
- [ ] Sources spot-checked

## Verification
- Spot-check cited sources; confirm excerpts match claims.

## Failure & recovery
| failure | recovery |
|---|---|
| false certainty | lower confidence |
| source dominance | require independent confirmation |
| weak evidence | say so; recommend an experiment |

## Escalation
- Irreconcilable contradictions on decision-critical facts.

## Handoff
- receives: research questions, raw findings
- passes: evidence synthesis with confidence and unknowns

## Evaluation
The org evaluates this skill by evidence quality, contradiction handling,
and confidence calibration — never by tone.

## Observability
- Record claims with provenance in the audit trail.

## References
- references/methodology.md — extraction and contradiction rules