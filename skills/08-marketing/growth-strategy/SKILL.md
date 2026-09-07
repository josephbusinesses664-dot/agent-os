---
id: growth-strategy
name: Growth Strategy
description: Design growth loops and experiments with honest measurement.
category: 08-marketing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [growth, loops, experiments]
compatible_agents: [growth-agent, marketing-director]
---

# Growth Strategy

## Purpose
Find repeatable, scalable ways to grow — loops over one-off pushes.

## Loop design
A growth loop: input → output that feeds the input.
Examples: content → SEO → traffic → signups → content; product usage →
sharing → invites → usage; community → Q&A → trust → signups.

For each candidate loop, estimate:
- **Input cost** — effort per unit (content piece, invite, share).
- **Conversion** — input → activation rate.
- **Output** — how much new input each activated user produces (virality, k-factor).
- **Time** — loop latency.

Pick loops where output > input with a healthy margin; run the numbers
honestly — a loop that needs 100% conversion doesn't exist.

## Rules
- Measure activation, not just signups.
- Kill loops that don't compound within the test window; double down on the ones that do.
- No fake incentives (forced invites) that poison retention.