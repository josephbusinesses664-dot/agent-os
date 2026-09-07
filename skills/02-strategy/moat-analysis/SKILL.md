---
id: moat-analysis
name: Moat Analysis
description: Assess defensibility of an advantage — how durable, how wide, and what erodes it.
category: 02-strategy
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [moat, defensibility, competitive]
compatible_agents: [competitor-analyst, product-director, executive]
---

# Moat Analysis

## Purpose
Evaluate how durable a competitive advantage is, and what would erode it.

## Moat types (assess each)
| Moat | Signal | Decay risk |
|---|---|---|
| Network effects | value grows with users; multi-sided | platform risk |
| Data | proprietary data compounds; hard to replicate | open alternatives |
| Switching costs | integration depth, stored workflows, data lock-in | standards |
| Brand/trust | preference without feature comparison | reputation events |
| Cost advantage | structurally cheaper delivery | commoditization |
| Distribution | owned channels, partnerships | channel disruption |
| Regulation/license | barriers to entry | policy change |

## Output
- Moat map: which moats exist, how wide (1-5), how durable (1-5).
- Erosion scenarios: what competitor moves or market shifts weaken it.
- Defense plan: 2-3 concrete actions to widen the durable moats.
- Honest verdict: "no moat yet" is acceptable — then state what would create one.

## Rules
- A feature is not a moat. Ask: "could a funded competitor copy this in 6 months?"
- Label each assessment with confidence and evidence.