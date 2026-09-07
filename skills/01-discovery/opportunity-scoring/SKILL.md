---
id: opportunity-scoring
name: Opportunity Scoring
description: Score and rank opportunities on a transparent, weighted rubric so the executive can prioritize.
category: 01-discovery
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [opportunity, scoring, prioritization]
compatible_agents: [executive, product-director, market-researcher]
---

# Opportunity Scoring

## Purpose
Turn messy opportunity data into a defensible ranking. The rubric is explicit
so a decision can be challenged and re-scored.

## Dimensions (0-5 each)
| Dimension | What it measures |
|---|---|
| Demand | evidence of need + willingness to pay |
| Market size | reachable audience / revenue ceiling |
| Competition | how contested the space is (lower = better) |
| Moat | defensibility once built (data, brand, network, cost) |
| Fit | alignment with capabilities and strategy |
| Timing | urgency and market readiness |
| Risk | execution, regulatory, technical risk (inverted) |

Weights are configurable; default: Demand 25%, Size 15%, Competition 15%,
Moat 15%, Fit 15%, Timing 10%, Risk 5%.

## Output
```markdown
| Rank | Opportunity | Demand | Size | Comp | Moat | Fit | Timing | Risk | Score |
| 1 | <name> | 4 | 3 | 2 | 3 | 4 | 4 | 4 | 3.55 |
```
Include a one-paragraph rationale per top-3 opportunity and the single biggest
unknown for each.

## Rules
- Show the math. A score without its components is a vibe.
- Re-score when new evidence arrives; record the delta.