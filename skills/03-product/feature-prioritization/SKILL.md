---
id: feature-prioritization
name: Feature Prioritization
description: Prioritize features on a transparent scorecard balancing value, cost, risk and evidence.
category: 03-product
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [prioritization, features, backlog]
compatible_agents: [product-manager, product-director, growth-agent]
---

# Feature Prioritization

## Purpose
Rank features so the team always works on the highest expected value first.

## Scorecard (0-5 each)
| Dimension | Question |
|---|---|
| User value | how much does it move the core job? |
| Business value | revenue/retention/defensibility impact |
| Evidence | demand or data supporting it |
| Effort | relative cost to build (inverted) |
| Risk | technical/compliance risk (inverted) |
| Strategic fit | alignment with the roadmap |

Score = weighted sum with explicit weights. Include a one-line rationale per
top feature and what evidence would change its rank.

## Anti-patterns to avoid
- Prioritizing by loudest stakeholder.
- Ignoring maintenance/tech-debt items.
- Never revisiting the ranking as evidence arrives.

## Rules
- Show the scorecard — "we did it because it scored X" beats "we felt like it".
- Re-score quarterly or when a big assumption breaks.