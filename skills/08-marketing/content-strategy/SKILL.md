---
id: content-strategy
name: Content Strategy
description: "Intent-driven content strategy — topics, formats, funnel stage, measurement — with evidence of demand."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [messaging, seo]
compatible_agents: [content-agent, seo-agent]
tags: [content, strategy, seo]
contract:
  prerequisites:
    - "the message spine and audience"
    - "content goals (traffic, leads, trust)"
  preferred_agents: [content-agent, seo-agent]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "topic selection backed by demand signals (search, community)"
  artifact_contract:
    - "content strategy (topics, formats, funnel mapping, metrics)"
  quality_gates:
    - "topics tied to audience intent, not keyword stuffing"
    - "content mapped to funnel stage"
    - "metrics defined per content type"
  verification:
    - "check topics have real demand signals"
  failure_modes:
    content_dump: "fewer, higher-value pieces aligned to intent"
    metric_missing: "define what each piece must achieve"
  escalation:
    - "content goals that require unsupported claims"
  handoff_in:
    - "message spine"
    - "audience"
  handoff_out:
    - "content strategy with topics and metrics"
  evaluation:
    - "topic-demand alignment"
    - "funnel mapping"
  observability:
    - "record topics and their demand evidence"
  related_skills: [seo, copywriting, social-content, messaging]
---

# Content Strategy

## Purpose
Choose what content to create, for whom, at which funnel stage, and how it
will be measured — driven by audience intent and demand evidence.

## When to use / When NOT to use
- use: content planning, SEO programs, launch content
- avoid: content calendars built by keyword-stuffing; avoid producing
  content with no defined job

## Inputs & assumptions
- inputs: message spine, audience, content goals
- assumptions: demand signals are evidence to gather, not to assume

## Workflow
1. State content goals (traffic / leads / trust / activation).
2. Collect demand signals for candidate topics (search, communities,
   questions people actually ask).
3. Map topics to funnel stages (awareness, consideration, decision).
4. Choose formats per intent (how-to, comparison, proof, reference).
5. Define the metric per content type (rankings, clicks, signups, shares).
6. Prioritize; fewer high-value pieces over a content dump.

## Evidence requirements
- Topic selection backed by demand signals; not guesses.

## Artifact contract
- `content-strategy`: topics (intent, demand evidence, funnel stage,
  format), metrics, priorities.

## Quality gates (definition of done)
- [ ] Topics tied to audience intent
- [ ] Content mapped to funnel stage
- [ ] Metrics defined per content type
- [ ] Demand evidence per topic

## Verification
- Check topics have real demand signals (search/community evidence).

## Failure & recovery
| failure | recovery |
|---|---|
| content dump | prioritize by intent and evidence |
| missing metrics | define what each piece must achieve |
| unsupported claims | escalate the claim gap |

## Escalation
- Content goals requiring unsupported claims — escalate.

## Handoff
- receives: message spine, audience
- passes: content strategy (topics, formats, metrics) to writers/SEO

## Evaluation
The org evaluates this skill by topic-demand alignment and funnel mapping.

## Observability
- Record topics and their demand evidence in the project.

## References
- references/patterns.md — topic clustering and intent mapping