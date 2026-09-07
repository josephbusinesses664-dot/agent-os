---
id: positioning
name: Positioning
description: "Evidence-based positioning — target, category, differentiation, proof — with a one-sentence statement."
category: 02-strategy
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [competitor-analysis, audience-research]
compatible_agents: [marketing-director, product-manager, growth-agent, content-agent]
tags: [positioning, messaging, differentiation]
contract:
  prerequisites:
    - "product understanding and target segment"
    - "competitor landscape (or the competitor-analysis skill ran)"
  preferred_agents: [marketing-director, product-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "differentiation claims backed by product evidence"
    - "target customer's language used, not invented"
  artifact_contract:
    - "positioning statement (target, category, differentiator, proof)"
  quality_gates:
    - "one-sentence positioning statement"
    - "differentiation is provable, not aspirational"
    - "target segment named precisely enough to reach"
  verification:
    - "test the statement against competitor claims — does it survive?"
  failure_modes:
    undifferentiated: "go back to product evidence; if none, say so"
    category_error: "re-examine what category customers actually shop"
  escalation:
    - "no provable differentiator — escalate the product gap"
  handoff_in:
    - "product understanding"
    - "target segment"
    - "competitor landscape"
  handoff_out:
    - "positioning statement"
    - "proof points"
    - "message spine for messaging/copy skills"
  evaluation:
    - "statement differentiates against real competitors"
    - "proof points are product-factual"
  observability:
    - "record the positioning statement as a project decision"
  related_skills: [messaging, marketing-strategy, competitor-analysis]
---

# Positioning

## Purpose
Decide, with evidence, how the product should be framed in the customer's
mind: for whom, against what, differentiated how, proven by what.

## When to use / When NOT to use
- use: before messaging, landing pages, pitches, or any external claim
- avoid: before product reality is understood; avoid positioning by wishful
  differentiation ("we're the only ones who care about quality")

## Inputs & assumptions
- inputs: product understanding, target segment, competitor landscape
- assumptions: segment assumptions must be labeled — positioning built on an
  assumed segment inherits that assumption

## Workflow
1. **Target** — the precise segment (who, what job, what pain).
2. **Category** — the category the customer actually shops in (not the one
   the team wishes existed).
3. **Differentiator** — the one provable difference that matters to this
   segment.
4. **Proof** — the evidence: feature, benchmark, case, or architecture. If
   there is no proof, the differentiator is aspirational — say so.
5. **Statement** — one sentence: "For [target], who [pain], [product] is the
   [category] that [differentiator], unlike [alternative]."

## Evidence requirements
- Differentiation claims are product-factual and testable.
- The target's language appears verbatim from research, not invented.

## Artifact contract
- `positioning-statement`: target, category, differentiator, proof points,
  alternatives framed against, message spine.

## Quality gates (definition of done)
- [ ] One-sentence statement
- [ ] Differentiator provable from product facts
- [ ] Segment precise enough to reach in a channel
- [ ] Statement survives a read against top competitor claims

## Verification
- Read the statement against each top competitor's homepage claim.
- Check every proof point is real product behavior.

## Failure & recovery
| failure | recovery |
|---|---|
| undifferentiated | return to product evidence; if none exists, escalate the gap |
| category mismatch | re-examine what category customers actually compare in |
| target too vague | tighten the segment from research, or flag the missing research |

## Escalation
- No provable differentiator — escalate as a product gap, not a messaging
  problem.

## Handoff
- receives: product understanding, target segment, competitor landscape
- passes: positioning statement, proof points, message spine

## Evaluation
The org evaluates this skill by whether the statement differentiates against
real competitors and whether proof points are product-factual.

## Observability
- Record the positioning statement as a project decision so downstream
  marketing skills use one consistent spine.

## References
- references/patterns.md — positioning statement variants and proof types