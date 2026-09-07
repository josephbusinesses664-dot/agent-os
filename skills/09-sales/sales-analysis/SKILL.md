---
id: sales-analysis
name: Sales Analysis
description: Quantitative sales analysis — metrics, cohorts, unit economics.
category: 09-sales
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [sales, analysis, metrics]
compatible_agents: [sales-analyst]
---

# Sales Analysis

## Purpose
Turn sales data into decisions: what's working, what's leaking, what to do.

## Core metrics
- Conversion by stage/source; CAC and payback; LTV (by cohort, not blended);
- win rate by segment/channel; ACV trends; churn & net retention;
- sales cycle length; activity ratios (touches → meetings → proposals).

## Method
1. Define the question; pick the metric that answers it.
2. Segment: by channel, segment, rep, month — the blend hides everything.
3. Cohort analysis for retention/LTV: same-month groups compared over time.
4. Compare against targets and trend; isolate the change that moved the number.
5. Recommend actions with owners; follow up on outcomes.

## Rules
- Show the numbers and the math; no vibes.
- Distinguish correlation from cause; propose experiments to confirm.