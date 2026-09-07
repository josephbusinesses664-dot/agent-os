---
id: demand-validation
name: Demand Validation
description: "Validate whether real demand exists before building — signals, willingness to pay, falsifiable tests."
category: 01-discovery
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [market-research]
compatible_agents: [market-researcher, product-researcher, product-manager]
tags: [demand, validation, signals, willingness-to-pay]
contract:
  prerequisites:
    - "a product hypothesis and a target customer segment"
    - "the decision this validation must inform (build / pivot / kill)"
  preferred_agents: [market-researcher, product-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "money signals (existing sales, pre-orders, paid adjacent tools)"
    - "behavior signals (recurring threads, search volume, job posts)"
    - "explicit asks and complaints, each with source and date"
    - "willingness-to-pay evidence or an explicit unknown"
  artifact_contract:
    - "demand-assessment report (signal inventory, confidence, verdict)"
  quality_gates:
    - "every claim labeled observed / inferred / assumed"
    - "no extrapolation from a single anecdote"
    - "falsifiable next test stated when demand is uncertain"
  verification:
    - "re-check each cited source resolves and matches the claim"
    - "confirm the verdict follows from the evidence, not the tone"
  failure_modes:
    no_evidence: "broaden search terms, add adjacent communities, then report low confidence instead of guessing"
    thin_sample: "label sample size, reduce confidence, recommend a falsifiable experiment"
  escalation:
    - "conflicting strong signals (e.g. money says yes, behavior says no)"
  handoff_in:
    - "product hypothesis"
    - "target segment"
  handoff_out:
    - "demand verdict"
    - "signal inventory with confidence"
    - "willingness-to-pay evidence"
    - "unknowns and recommended experiment"
  evaluation:
    - "distinguish real demand from hype"
    - "identify the strongest evidence in the set"
    - "flag insufficient evidence instead of fabricating a verdict"
  observability:
    - "record sources consulted and confidence per signal"
  related_skills: [opportunity-scoring, market-research, reddit-research]
---

# Demand Validation

## Purpose
Determine whether enough people want this enough to pay, before committing
build resources. Prefer falsifiable checks over opinions.

## When to use / When NOT to use
- use: before building, before committing budget, when choosing between ideas
- avoid: when the question is "how big is this market" (use market-sizing);
  do not run a full validation for trivial internal tooling

## Inputs & assumptions
- inputs: product hypothesis, target segment, decision deadline
- assumptions: state every assumption (e.g. "segment = indie developers") and
  label it assumed until evidence arrives

## Signal hierarchy (strongest first)
1. **Money** — existing sales, pre-orders, paid tools solving adjacent problems.
2. **Behavior** — recurring forum/community threads, upvotes, search volume
   trends, job posts.
3. **Explicit asks** — feature requests, "is there a tool for X" posts.
4. **Complaints** — recurring pain with existing solutions.
5. **Attention** — engagement on related content (weakest, cheapest).

## Workflow
1. Restate the decision this validation must inform — the report is judged by
   how well it enables that decision.
2. Generate competing hypotheses (real demand / small niche / hype-only) and
   hunt evidence for and against each — never only confirming evidence.
3. Collect signals per the hierarchy with source, date and verbatim excerpt.
4. Check for money/behavior signals specifically — they outrank opinions.
5. Label every claim: observed (you saw it), inferred (you reasoned it),
   assumed (you took it as given).
6. Produce the verdict with a confidence level and the single best falsifiable
   test that would change the verdict.

## Evidence requirements
- Each signal: source, source_type, retrieval date, claim, excerpt, confidence.
- Weak evidence is reported as weak — lower the confidence, never inflate it
  because the model sounds certain.

## Artifact contract
- `demand-assessment` report: hypothesis, segment, signal inventory (with
  sources), verdict, confidence, recommended experiment.

## Quality gates (definition of done)
- [ ] Every claim labeled observed / inferred / assumed
- [ ] Money or behavior signals present, or explicitly stated as absent
- [ ] No single-anecdote extrapolation
- [ ] Verdict maps to the evidence table
- [ ] Falsifiable next test stated when demand is uncertain

## Verification
- Re-check that each cited source resolves and supports the claim it is cited
  for.
- Sanity-check the verdict against the strongest signal, not the noisiest.

## Failure & recovery
| failure | recovery |
|---|---|
| no evidence found | broaden terms, add adjacent communities, then report low confidence |
| thin sample (1-3 threads) | label it, reduce confidence, recommend a falsifiable experiment |
| contradictory signals | preserve both, investigate the money signals, escalate |

## Escalation
- Conflicting strong signals, or a verdict that would commit significant
  budget while evidence stays weak — escalate with both sides presented.

## Handoff
- receives: product hypothesis, target segment
- passes: demand verdict, signal inventory with confidence,
  willingness-to-pay evidence, unknowns, recommended experiment

## Evaluation
The org evaluates this skill by whether the report distinguishes real demand
from hype, cites the strongest evidence correctly, and flags insufficient
evidence rather than fabricating a verdict.

## Observability
- Trace the sources consulted, the confidence per signal, and the final
  verdict so a reviewer can replay the reasoning.

## References
- references/methodology.md — signal interpretation and common failure modes