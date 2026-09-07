---
id: sentiment-analysis
name: Sentiment Analysis
description: Assess sentiment in community text — tone, trend, drivers — with honesty about limits.
category: 19-community-intelligence
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [sentiment, analysis, tone]
compatible_agents: [community-researcher, market-researcher]
---

# Sentiment Analysis

## Purpose
Gauge how people feel about a topic/product — and why — so positioning and
product work address the real drivers.

## Method
1. **Sample** — a defined window and source set (threads, reviews, mentions);
   report the sample size.
2. **Label** — positive / negative / mixed / neutral per item, with the
   quoted reason (sentiment without the reason is useless).
3. **Themes** — group the *reasons* behind sentiment: price, UX, support,
   reliability, feature gaps.
4. **Trend** — compare windows; is sentiment improving or decaying?
5. **Intensity** — strong language and engagement weight the signal.

## Honesty rules
- Sentiment is directional, not precise: report "mostly positive with a
  recurring reliability complaint", not "87.3% satisfaction" from 40 posts.
- Separate *sentiment about the product* from *sentiment about the category*.
- Confirmation bias: include counter-examples explicitly.

## Output
Sentiment brief: overall tone, the top positive drivers, top negative drivers
(with quotes), trend, and the product/marketing implications.