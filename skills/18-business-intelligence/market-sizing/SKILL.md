---
id: market-sizing
name: Market Sizing
description: Estimate market size (TAM/SAM/SOM) with explicit assumptions and ranges.
category: 18-business-intelligence
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [market, sizing, tam]
compatible_agents: [market-researcher, product-researcher]
---

# Market Sizing

## Purpose
Estimate how big an opportunity really is — useful for prioritization, not
for false precision.

## Method
1. **TAM (top-down and bottom-up)** — top-down: total spend in the category;
   bottom-up: #potential buyers × average annual value. Cross-check both.
2. **SAM** — the portion you can reach with your product/channel within your
   geography/segment.
3. **SOM** — the share you can realistically capture in 3-5 years given
   competition and distribution.

## Presentation
```markdown
- TAM: $X–$Y (assumptions: ...)
- SAM: $X–$Y (assumptions: ...)
- SOM: $X–$Y (assumptions: ...)
- Key unknowns: ...
```
Always ranges, always assumptions, always a bottom-up cross-check.

## Rules
- A single precise number ("$4.2B market") without assumptions is a guess
  with a suit on. Refuse to produce one.
- Size the *problem*, not the category: buyers with the pain × willingness
  to pay beats "everyone in industry X".