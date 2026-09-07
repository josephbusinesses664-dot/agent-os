---
id: moat-analysis
name: Moat Analysis
description: "Assess defensibility — what protects this business from competition, with evidence per moat type."
category: 02-strategy
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [competitor-analysis]
compatible_agents: [executive, chief-of-staff, product-director]
tags: [moat, defensibility, competition, strategy]
contract:
  prerequisites:
    - "the business model and competitive landscape under analysis"
  preferred_agents: [executive, chief-of-staff]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "each moat claim backed by evidence or labeled hypothesis"
    - "competitor copying difficulty assessed, not assumed"
  artifact_contract:
    - "moat assessment (per-moat-type evidence, overall defensibility verdict)"
  quality_gates:
    - "moat types examined: network effects, switching costs, brand, data, scale, regulation, IP"
    - "no moat asserted without a mechanism and evidence"
  verification:
    - "for each claimed moat, ask: what stops a well-funded copycat?"
  failure_modes:
    no_evidence: "label the moat as hypothesized and testable"
    copycat_ignored: "explicitly reason about the copycat timeline"
  escalation:
    - "businesses whose only moat is 'being first' when capital follows"
  handoff_in:
    - "business model"
    - "competitive landscape"
  handoff_out:
    - "moat assessment with per-type evidence and verdict"
  evaluation:
    - "mechanism-first reasoning"
    - "correct skepticism of weak moats"
  observability:
    - "record moat verdicts and their evidence basis"
  related_skills: [competitor-analysis, business-strategy, positioning]
---

# Moat Analysis

## Purpose
Assess defensibility: what protects this business from competition over time?
For each candidate moat, give the mechanism, the evidence, and the copycat
test.

## When to use / When NOT to use
- use: before committing to a competitive market, before pricing decisions,
  in investor/pitch preparation
- avoid: for internal tools with no external competition; avoid producing a
  moat verdict without a mechanism

## Inputs & assumptions
- inputs: business model, competitive landscape
- assumptions: label "we could build this" claims as assumptions unless
  evidenced

## Moat types to examine
1. **Network effects** — does value grow with users? evidence of density.
2. **Switching costs** — what locks customers in? measured or estimated.
3. **Brand/trust** — in commoditized categories, brand matters; evidence?
4. **Data** — proprietary data that compounds; who else has it?
5. **Scale economies** — cost advantage at volume; current evidence.
6. **Regulation/IP** — licenses, patents, compliance barriers.
7. **Distribution** — owned channels competitors cannot easily buy.

## Workflow
1. List the moat types plausibly available to this business.
2. For each: mechanism → evidence → copycat test (what stops a well-funded
   copycat in 18 months?).
3. Weigh the portfolio: is defensibility concentrated or diversified?
4. Produce the verdict: strong / mixed / weak, with the reasoning.

## Evidence requirements
- Every moat claim has a mechanism and evidence (or is labeled a testable
  hypothesis).
- Competitor copying difficulty is reasoned, not assumed.

## Artifact contract
- `moat-assessment`: per-type mechanism + evidence + copycat test, portfolio
  verdict, implications.

## Quality gates (definition of done)
- [ ] All relevant moat types examined
- [ ] No moat asserted without mechanism and evidence
- [ ] Copycat test applied to the strongest claimed moat
- [ ] Verdict follows from the evidence

## Verification
- For the strongest claimed moat, run the copycat test explicitly.
- Check that "first mover" is not treated as a moat by itself.

## Failure & recovery
| failure | recovery |
|---|---|
| no evidence of defensibility | label moats as hypotheses, recommend a test |
| copycat timeline ignored | reason it explicitly and fold into the verdict |
| moat list padded | drop weak entries, keep only mechanism-backed ones |

## Escalation
- A strategy that depends on a weak or absent moat — escalate with the
  copycat analysis so leadership decides consciously.

## Handoff
- receives: business model, competitive landscape
- passes: moat assessment (mechanism, evidence, copycat test, verdict)

## Evaluation
The org evaluates this skill by mechanism-first reasoning and correct
skepticism of weak moats — "being first" is not defensibility.

## Observability
- Record moat verdicts with their evidence basis in the decision log.

## References
- references/methodology.md — copycat test and moat evidence grading