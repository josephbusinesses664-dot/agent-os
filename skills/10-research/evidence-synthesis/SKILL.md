---
id: evidence-synthesis
name: Evidence Synthesis
description: Combine evidence from many sources into a defensible conclusion with uncertainty labeled.
category: 10-research
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [synthesis, evidence, research]
compatible_agents: [research-director, market-researcher]
---

# Evidence Synthesis

## Purpose
Turn many sources into one defensible conclusion — with disagreement,
uncertainty and gaps reported honestly.

## Method
1. **Collect** — every relevant claim as: claim | source | date | type
   (primary/secondary/opinion).
2. **Assess quality** — source authority, recency, bias, methodology.
3. **Cross-check** — find corroboration and contradiction; where sources
   disagree, report both with weights.
4. **Weight** — primary + recent + authoritative > anecdote.
5. **Conclude** — a conclusion with explicit confidence (high/medium/low) and
   the reasoning chain.
6. **Report gaps** — what's unknown and what would change the conclusion.

## Output
```markdown
## Conclusion (confidence: X)
## Supporting evidence (weighted)
## Disagreements
## Unknowns / would-change-the-answer factors
```

## Rules
- A synthesis without confidence labels is a guess wearing a lab coat.
- Never average sources into false certainty — disagreements are findings.