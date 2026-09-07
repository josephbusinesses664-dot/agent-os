---
id: business-model-analysis
name: Business Model Analysis
description: Analyze and stress-test business models — revenue, costs, unit economics, risks.
category: 18-business-intelligence
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [business-model, unit-economics]
compatible_agents: [executive, market-researcher, sales-analyst]
---

# Business Model Analysis

## Purpose
Test whether a business model makes money: the math must work at the unit
level before the story matters.

## Analysis
1. **Revenue model** — the streams, with the pricing skill's value anchor.
2. **Cost structure** — COGS, acquisition, fixed/operating; where scale helps
   and where it hurts.
3. **Unit economics** — per customer: LTV, CAC, payback period, gross margin;
   show assumptions and ranges.
4. **Sensitivity** — what breaks the model: churn ±5pp, CAC +50%, price -20%?
5. **Break-even** — the volume/price combination where the model sustains.
6. **Risk & defensibility** — competitors can price below? retention cliffs?

## Output
Model brief with the numbers, the 3 biggest risks to the math, and the
experiments that would validate the assumptions.

## Rules
- Show every assumption — a model you can't interrogate isn't analysis.
- Pessimistic case included: plan for it or say why it can't happen.