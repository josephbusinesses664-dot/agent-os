---
id: pricing-monetization
name: Pricing & Monetization
description: "Evidence-driven pricing — willingness to pay, models, anchors, experiments — with labeled economics."
category: 02-strategy
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [business-strategy, market-research]
compatible_agents: [executive, product-manager, sales-director]
tags: [pricing, monetization, revenue]
contract:
  prerequisites:
    - "customer segment and willingness-to-pay evidence (or an explicit gap)"
    - "unit economics (COGS, CAC inputs) or a labeled placeholder"
  preferred_agents: [executive, product-manager]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "willingness to pay evidenced or explicitly unknown"
    - "competitor pricing gathered with source and date"
    - "every financial figure labeled observed / calculated / estimated / assumed"
  artifact_contract:
    - "pricing recommendation (model, anchors, numbers, experiment plan)"
  quality_gates:
    - "no price recommended without a stated basis"
    - "pricing experiment defined when evidence is thin"
    - "no invented financial data"
  verification:
    - "check competitor prices against their current pricing pages"
  failure_modes:
    no_wtp: "recommend a pricing experiment instead of a confident number"
    anchor_errors: "re-check anchors against current sources"
  escalation:
    - "price changes that affect existing customers (grandfathering decision)"
  handoff_in:
    - "segment and willingness-to-pay evidence"
    - "unit economics"
  handoff_out:
    - "pricing recommendation with model, anchors, numbers, experiment plan"
  evaluation:
    - "every number labeled and sourced"
    - "experiment-first when evidence is thin"
  observability:
    - "record the pricing decision and its evidence in the decision log"
  related_skills: [business-strategy, sales-strategy, market-sizing]
---

# Pricing & Monetization

## Purpose
Recommend a pricing model and numbers from evidence — willingness to pay,
competitive anchors, economics — and define the experiment when evidence is
thin.

## When to use / When NOT to use
- use: before launch, before changing prices, when a new tier is proposed
- avoid: without a customer segment and any WTP signal; avoid inventing a
  "market standard" number from memory

## Inputs & assumptions
- inputs: segment, WTP evidence, unit economics
- assumptions: every financial figure is labeled observed / calculated /
  estimated / assumed

## Workflow
1. **Customer & value** — what is the job, what does solving it save/earn?
2. **Willingness to pay** — collect evidence: competitor prices, existing
   pricing pages, community mentions of price, pre-order history. If none,
   the deliverable is an experiment, not a confident price.
3. **Model choice** — one-time / subscription / usage / hybrid; match the
   model to the value metric the customer perceives.
4. **Anchors** — gather competitor price points with source + date; position
   relative to them deliberately (premium / value / undercut).
5. **Economics** — COGS, CAC, target gross margin; check the price supports
   them; label every input.
6. **Recommendation + experiment** — the price, the rationale, the metric
   that will validate it, and the change trigger.

## Evidence requirements
- WTP evidenced or explicitly unknown — never asserted.
- Competitor prices carry source + retrieval date; re-verify before
  finalizing.
- All financial figures labeled.

## Artifact contract
- `pricing-recommendation`: model, value metric, price points, anchors with
  sources, economics check, experiment plan.

## Quality gates (definition of done)
- [ ] No price recommended without a stated basis
- [ ] Every number labeled observed / calculated / estimated / assumed
- [ ] Pricing experiment defined when WTP evidence is thin
- [ ] Existing-customer impact considered

## Verification
- Re-check competitor prices against their current pricing pages.
- Recompute margin from the stated economics.

## Failure & recovery
| failure | recovery |
|---|---|
| no WTP evidence | deliver an experiment design, not a fabricated price |
| stale anchors | re-fetch pricing pages, label vintage |
| margin impossible at anchor | surface the tension — pricing or economics must give |

## Escalation
- Price changes affecting existing customers — escalate the grandfathering
  decision with the revenue impact.

## Handoff
- receives: segment, WTP evidence, unit economics
- passes: pricing recommendation (model, anchors, numbers, experiment plan)

## Evaluation
The org evaluates this skill by labeled, sourced numbers and by
experiment-first behavior when WTP evidence is thin.

## Observability
- Record the pricing decision, anchors, and experiment plan in the decision
  log.

## References
- references/methodology.md — pricing models and WTP evidence sources