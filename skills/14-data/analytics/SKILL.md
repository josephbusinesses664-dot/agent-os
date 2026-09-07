---
id: analytics
name: Analytics
description: Analysis with rigor — metrics definition, cohort thinking, honest reporting.
category: 14-data
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [analytics, metrics, data]
compatible_agents: [sales-analyst, market-researcher]
---

# Analytics

## Purpose
Answer questions with data honestly: define the metric, segment properly,
check the math, report uncertainty.

## Method
1. **Define** — the metric's exact formula (numerator, denominator, window);
   a metric nobody can define precisely is not a metric.
2. **Segment** — overall numbers hide everything; cut by cohort, channel,
   segment, time.
3. **Compare** — vs. baseline/previous period/expectation; state the baseline.
4. **Check** — sanity checks: totals, units, timestamps, duplicates.
5. **Uncertainty** — small samples → wide error bars; say so.
6. **Recommend** — what the data implies for a decision; never "interesting"
   without an action.

## Rules
- Never cherry-pick windows to tell a story; pre-register the analysis window.
- Correlation ≠ causation: propose the test that would confirm.
- Charts label axes and units; a chart that can't be read without the author
  is decoration.