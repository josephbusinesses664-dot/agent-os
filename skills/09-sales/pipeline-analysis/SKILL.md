---
id: pipeline-analysis
name: Pipeline Analysis
description: Diagnose the sales pipeline — funnel shape, stage aging, conversion, blockers.
category: 09-sales
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [pipeline, funnel, analysis]
compatible_agents: [sales-analyst, sales-director]
---

# Pipeline Analysis

## Purpose
Find where deals stall and what to do about it — with numbers.

## Analysis
1. **Funnel shape** — conversion per stage vs. targets; where's the biggest
   leak (creation → qualification → demo → proposal → close)?
2. **Stage aging** — deals stuck in a stage beyond expected duration = pipeline
   rot; flag and act.
3. **Win/loss** — reasons for losses (price, fit, competitor, timing) grouped;
   feed back to product/marketing.
4. **Forecast honesty** — commit = qualified + agreed timeline + economic buyer;
   anything else is pipeline, not forecast.
5. **Actions** — concrete: re-qualify stale deals, fix the leaky stage
   (process, content, pricing), adjust targets.

## Output
Pipeline brief with the numbers, the diagnosis, and 3 prioritized actions —
each with an owner and a review date.