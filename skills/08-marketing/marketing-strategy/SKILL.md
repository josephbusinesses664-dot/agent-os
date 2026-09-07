---
id: marketing-strategy
name: Marketing Strategy
description: "Hypothesis-driven marketing strategy — channels, messaging, funnel, experiments — with measurement."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [positioning, audience-research]
compatible_agents: [marketing-director, growth-agent]
tags: [marketing, strategy, gtm]
contract:
  prerequisites:
    - "the product and its stage"
    - "audience research (or the explicit gap)"
  preferred_agents: [marketing-director, growth-agent]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "channel choices tied to audience evidence"
    - "every hypothesis has a measurement"
  artifact_contract:
    - "marketing strategy (channels, message, funnel, experiments, metrics)"
  quality_gates:
    - "channels selected from audience location, not habit"
    - "one message spine"
    - "funnel metrics defined with a north-star"
    - "each tactic is a testable hypothesis with measurement"
  verification:
    - "check each hypothesis has a metric that could falsify it"
  failure_modes:
    channel_dump: "master 2-3 channels; ignore the rest until proven"
    metric_vibes: "pick countable metrics"
  escalation:
    - "strategy depending on unproven channel economics"
  handoff_in:
    - "product"
    - "audience research"
  handoff_out:
    - "marketing strategy with experiments and metrics"
  evaluation:
    - "hypothesis testability"
    - "channel-audience alignment"
  observability:
    - "record strategy and experiment plan"
  related_skills: [positioning, messaging, audience-research, content-strategy]
---

# Marketing Strategy

## Purpose
Decide where and how to win attention: channels, message spine, funnel, and
metrics — as testable hypotheses with measurements, grounded in the product
and its audience.

## When to use / When NOT to use
- use: GTM planning, launch strategy, growth planning
- avoid: without audience research (or the explicit gap flagged); avoid
  marketing plans with no measurement

## Inputs & assumptions
- inputs: product, audience research
- assumptions: budget and channel economics assumed unless evidenced —
  label them

## Workflow
1. **Product reality** — what it is, the core job, current proof.
2. **Audience** — segments by pain and buying behavior (from audience
   research); where they gather.
3. **Channel selection** — pick 2-3 channels to master based on audience
   location and budget; ignore the rest until the first ones work.
4. **Message spine** — one message across channels (see positioning).
5. **Funnel & metrics** — awareness → activation → revenue; one north-star
   metric; per-stage countable metrics.
6. **Experiments** — every tactic as a hypothesis with a falsifiable
   measurement.
7. **Review** — check the plan can be falsified; if not, fix it.

## Evidence requirements
- Channel choices tied to audience evidence.
- Every hypothesis has a metric that could falsify it.

## Artifact contract
- `marketing-strategy`: channels (with rationale), message spine, funnel,
  metrics, experiment plan.

## Quality gates (definition of done)
- [ ] Channels selected from audience location
- [ ] One message spine
- [ ] North-star + per-stage metrics defined
- [ ] Each tactic falsifiable

## Verification
- Check each hypothesis has a metric.

## Failure & recovery
| failure | recovery |
|---|---|
| channel dump | master 2-3; park the rest |
| metric vibes | pick countable metrics |
| unproven economics | label the assumption; design the test |

## Escalation
- Strategy depending on unproven channel economics — escalate with the
  assumption and the test.

## Handoff
- receives: product, audience research
- passes: marketing strategy (channels, message, funnel, experiments,
  metrics) to content/social/SEO

## Evaluation
The org evaluates this skill by hypothesis testability and
channel-audience alignment.

## Observability
- Record the strategy and experiment plan in the project.

## References
- references/patterns.md — channel selection and metric definitions