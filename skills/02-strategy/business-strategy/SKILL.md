---
id: business-strategy
name: Business Strategy
description: "Operator-grade strategy: decision, rationale, evidence, explicit assumptions, risks, alternatives, next action."
category: 02-strategy
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [market-research, strategy]
compatible_agents: [executive, chief-of-staff, product-director]
tags: [strategy, business-model, decisions]
contract:
  prerequisites:
    - "the decision to be made and its timeframe"
    - "available evidence (market, product, finance) or an explicit gap"
  preferred_agents: [executive, chief-of-staff]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "every recommendation grounded in evidence or labeled assumption"
    - "financial estimates labeled observed / calculated / estimated / assumed"
  artifact_contract:
    - "strategy memo (decision, rationale, evidence, assumptions, risks, alternatives, next action)"
  quality_gates:
    - "decision stated in one sentence"
    - "at least one alternative explicitly considered"
    - "no invented financial data"
    - "risks listed with mitigations"
  verification:
    - "re-read the memo: does the rationale follow from the evidence?"
    - "check every number has a label"
  failure_modes:
    missing_evidence: "state the gap and the experiment that would fill it"
    assumption_heavy: "flag assumption density and reduce confidence accordingly"
  escalation:
    - "high-stakes decisions with unresolved evidence gaps"
  handoff_in:
    - "decision context"
    - "available evidence"
  handoff_out:
    - "strategy memo with decision, rationale, risks, next action"
  evaluation:
    - "decision clarity"
    - "assumptions explicit and labeled"
    - "alternatives considered"
  observability:
    - "record the decision, alternatives, and confidence in the decision log"
  related_skills: [strategy, moat-analysis, positioning, market-sizing]
---

# Business Strategy

## Purpose
Produce operator-grade strategy: a clear decision, the rationale, the
evidence, explicit assumptions, risks, alternatives and the next action.

## When to use / When NOT to use
- use: major direction decisions (enter/exit, build/buy, pricing model,
  resourcing)
- avoid: routine execution questions (use the relevant department skill);
  avoid generating "strategy" without a decision attached

## Inputs & assumptions
- inputs: decision, timeframe, available evidence
- assumptions: list every assumption (customer, economics, timing) and label
  it; a strategy that hides its assumptions is unfalsifiable

## Framework (consider each explicitly)
- customer and problem
- alternative to the recommendation
- value delivered and captured
- distribution and channel
- competition and moat
- economics: pricing, CAC, retention, switching costs
- timing and execution difficulty
- risk and reversibility

## Workflow
1. State the decision in one sentence.
2. Gather the evidence that bears on it; note gaps explicitly.
3. Reason through the framework, labeling each element
   observed/calculated/estimated/assumed.
4. Consider at least one alternative seriously — write its best case.
5. Draft the memo: decision, rationale, evidence, assumptions, risks with
   mitigations, alternatives, next action.
6. Re-read for the trap: confident tone replacing missing evidence.

## Evidence requirements
- Every recommendation is grounded in evidence or explicitly labeled
  assumption.
- Numbers: observed (measured), calculated (derived from observed),
  estimated (judgment), assumed (taken as given). Never invent financial data.

## Artifact contract
- `strategy-memo`: decision (one sentence), rationale, evidence table,
  assumptions, risks+mitigations, alternatives, next action.

## Quality gates (definition of done)
- [ ] Decision stated in one sentence
- [ ] ≥1 alternative explicitly considered
- [ ] No invented financial data; every number labeled
- [ ] Risks listed with mitigations
- [ ] Next action concrete and owned

## Verification
- Re-read: does the rationale follow from the evidence table?
- Check the next action is concrete enough to plan a task.

## Failure & recovery
| failure | recovery |
|---|---|
| missing evidence | state the gap and the experiment that fills it; do not paper over |
| assumption-heavy | flag density, reduce confidence, mark the memo as provisional |
| alternatives not obvious | brainstorm 2-3, including the "do nothing" option |

## Escalation
- High-stakes decisions with unresolved evidence gaps — escalate with the
  decision, both sides of the gap, and a proposed experiment.

## Handoff
- receives: decision context, available evidence
- passes: strategy memo (decision, rationale, evidence, assumptions, risks,
  alternatives, next action)

## Evaluation
The org evaluates this skill by decision clarity, explicit labeled
assumptions, and genuine consideration of alternatives — not by how decisive
the prose sounds.

## Observability
- Record the decision, alternatives considered, and confidence in the
  project decision log.

## References
- references/methodology.md — assumption labeling and strategy anti-patterns