---
id: social-content
name: Social Content
description: "Channel-adapted social content from the message spine — claims accurate, format-native, measurable."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [messaging, copywriting]
compatible_agents: [social-agent, content-agent]
tags: [social, content, community]
contract:
  prerequisites:
    - "the message spine and target channels"
  preferred_agents: [social-agent, content-agent]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "claims product-factual; format adapted per channel"
  artifact_contract:
    - "social content (posts per channel, claims, CTA, metrics)"
  quality_gates:
    - "claim accuracy"
    - "channel-native format"
    - "clear CTA or intent per post"
  verification:
    - "re-read each post from the platform's audience perspective"
  failure_modes:
    repost_everywhere: "adapt format and length per channel"
    overclaim: "pull back to product proof"
  escalation:
    - "posts requiring unsupported claims"
  handoff_in:
    - "message spine"
    - "channels"
  handoff_out:
    - "social content with metrics"
  evaluation:
    - "channel adaptation"
    - "claim accuracy"
  observability:
    - "record posts and their intent"
  related_skills: [messaging, copywriting, content-strategy]
---

# Social Content

## Purpose
Produce channel-native social content from the message spine — accurate
claims, adapted format and length per platform, clear intent per post.

## When to use / When NOT to use
- use: organic/social publishing
- avoid: reposting the same text everywhere; avoid unsupported claims

## Inputs & assumptions
- inputs: message spine, channels
- assumptions: platform conventions assumed — check the platform before
  assuming format

## Workflow
1. State the intent per post (educate, engage, convert).
2. Adapt the message to the channel: length, format, tone, hashtags/links
   as native.
3. Attach proof to claims; cut claims without proof.
4. Write a clear CTA or engagement hook per post.
5. Define the metric per post (clicks, replies, shares).

## Evidence requirements
- Claims product-factual; the CTA/intent explicit.

## Artifact contract
- `social-content`: posts (channel, intent, claims, CTA), metrics.

## Quality gates (definition of done)
- [ ] Claim accuracy
- [ ] Channel-native format
- [ ] Clear intent per post
- [ ] Metrics defined

## Verification
- Re-read each post from the platform audience's perspective.

## Failure & recovery
| failure | recovery |
|---|---|
| repost everywhere | adapt per channel |
| overclaim | pull back to proof |
| weak hook | sharpen the opening |

## Escalation
- Posts requiring unsupported claims.

## Handoff
- receives: message spine, channels
- passes: social content with metrics

## Evaluation
The org evaluates this skill by channel adaptation and claim accuracy.

## Observability
- Record posts and their intent in the project.

## References
- references/patterns.md — per-channel format rules