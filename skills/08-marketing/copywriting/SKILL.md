---
id: copywriting
name: Copywriting
description: "Conversion-aware copy from the message spine — claims accurate, audience language, call to action — verified."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [messaging, positioning]
compatible_agents: [content-agent, growth-agent]
tags: [copy, writing, conversion]
contract:
  prerequisites:
    - "message spine and the piece's goal"
  preferred_agents: [content-agent, growth-agent]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "every claim traceable to product proof"
  artifact_contract:
    - "copy (headline, body, CTA) with claim notes"
  quality_gates:
    - "claims product-factual"
    - "single clear CTA per piece"
    - "audience language, not jargon"
    - "reads for the target reader, not the writer"
  verification:
    - "re-read as the customer: is the value instant and credible?"
  failure_modes:
    overclaim: "pull back to proven claims"
    feature_speak: "translate features to outcomes"
  escalation:
    - "copy that requires unsupported claims"
  handoff_in:
    - "message spine"
    - "piece goal"
  handoff_out:
    - "copy with claim and CTA notes"
  evaluation:
    - "claim accuracy"
    - "value clarity"
  observability:
    - "record the piece and its goal"
  related_skills: [messaging, landing-page-design, social-content]
---

# Copywriting

## Purpose
Write conversion-aware copy from the message spine: accurate claims, the
audience's language, outcomes over features, and one clear call to action.

## When to use / When NOT to use
- use: landing pages, ads, emails, posts
- avoid: writing without the message spine or piece goal; avoid overclaiming

## Inputs & assumptions
- inputs: message spine, piece goal
- assumptions: audience vocabulary assumed unless researched — label it

## Workflow
1. State the piece's goal (the action the reader should take).
2. Draft the value proposition in outcome terms (job done, pain removed).
3. Write headline → body → CTA with the audience's vocabulary.
4. Attach proof to claims; cut any claim without proof.
5. Re-read as the customer: instant value, credible claims, one CTA.

## Evidence requirements
- Every claim traceable to product proof; unsupported claims removed.

## Artifact contract
- `copy`: headline, body, CTA, claim notes, goal restated.

## Quality gates (definition of done)
- [ ] Claims product-factual
- [ ] One clear CTA
- [ ] Audience language
- [ ] Value instant and credible on first read

## Verification
- Re-read as the target customer.

## Failure & recovery
| failure | recovery |
|---|---|
| overclaim | pull back to proven claims |
| feature speak | translate to outcomes |
| weak CTA | make the next step obvious |

## Escalation
- Copy requiring unsupported claims — escalate the claim gap.

## Handoff
- receives: message spine, piece goal
- passes: copy with claim and CTA notes

## Evaluation
The org evaluates this skill by claim accuracy and value clarity.

## Observability
- Record the piece, its goal, and claim notes.

## References
- references/patterns.md — outcome framing and CTA patterns