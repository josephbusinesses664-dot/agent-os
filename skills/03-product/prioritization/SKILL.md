---
id: prioritization
name: Prioritization
description: General prioritization framework for projects, tasks, features and risks.
category: 03-product
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [prioritization, decision]
compatible_agents: [executive, product-director, operations-director, project-manager]
---

# Prioritization

## Purpose
Decide what to do next with a transparent, defensible method.

## Framework
1. **List** — all candidate items (features, tasks, risks, requests).
2. **Score** — each item on impact (0-5) and urgency (0-5); record the basis.
3. **Effort** — estimate relative effort; compute impact-per-effort.
4. **Dependencies** — mark items that unblock others.
5. **Cut line** — decide what is explicitly NOT doing this cycle.
6. **Review triggers** — what evidence changes the ranking.

## Rules
- Never "prioritize everything": a list where everything is high priority is
  unprioritized.
- Tie scores to evidence (metrics, deadlines, risk), not feelings.
- Publish the ranking and the cut line; revisit on new evidence.
- Record the decision in the decision log when it's consequential.