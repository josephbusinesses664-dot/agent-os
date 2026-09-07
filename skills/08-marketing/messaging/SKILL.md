---
id: messaging
name: Messaging
description: "Message spine from positioning — claims, proof, language — with evidence and channel adaptation."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [positioning, audience-research]
compatible_agents: [content-agent, growth-agent, copywriter]
tags: [messaging, copy, positioning]
contract:
  prerequisites:
    - "positioning statement and audience language"
  preferred_agents: [content-agent, growth-agent]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "every claim in the message backed by product proof"
  artifact_contract:
    - "message spine (claims, proof, language, channel variants)"
  quality_gates:
    - "claims are product-factual"
    - "language matches the audience's vocabulary"
    - "message consistent across channels"
  verification:
    - "check each claim against product reality"
  failure_modes:
    overclaim: "pull claims back to what the product proves"
    jargon: "translate to audience language"
  escalation:
    - "claims the product cannot yet support"
  handoff_in:
    - "positioning statement"
    - "audience language"
  handoff_out:
    - "message spine for copy/content"
  evaluation:
    - "claim accuracy"
    - "audience-language fit"
  observability:
    - "record the message spine as a project decision"
  related_skills: [positioning, copywriting, content-strategy]
---

# Messaging

## Purpose
Build a message spine from positioning: the claims, their proof, the
audience's language, and how the message adapts per channel — without
overclaiming.

## When to use / When NOT to use
- use: before copywriting, landing pages, campaigns
- avoid: inventing claims the product cannot prove; avoid messaging in
  company jargon

## Inputs & assumptions
- inputs: positioning statement, audience language
- assumptions: audience vocabulary assumed unless researched — label it

## Workflow
1. Extract the claims the positioning implies.
2. Attach product proof to every claim; cut claims without proof.
3. Rewrite in the audience's language (verbatim vocabulary).
4. Build the message spine: one core claim, supporting claims, proof
   points.
5. Adapt per channel (length, tone) without changing the spine.
6. Verify: every claim survives a product check.

## Evidence requirements
- Every claim backed by product proof; claims without proof are cut or
  labeled aspirational.

## Artifact contract
- `message-spine`: core claim, supporting claims, proof points, language
  notes, channel variants.

## Quality gates (definition of done)
- [ ] Claims product-factual
- [ ] Language matches audience vocabulary
- [ ] Message consistent across channels
- [ ] Proof attached per claim

## Verification
- Check each claim against product reality.

## Failure & recovery
| failure | recovery |
|---|---|
| overclaim | pull back to proven claims |
| jargon | translate to audience language |
| inconsistent spine | unify; channel variants keep the core claim |

## Escalation
- Claims the product cannot support — escalate the product gap.

## Handoff
- receives: positioning, audience language
- passes: message spine to copywriting and content

## Evaluation
The org evaluates this skill by claim accuracy and audience-language fit.

## Observability
- Record the message spine as a project decision.

## References
- references/patterns.md — claim-proof structures and channel adaptation