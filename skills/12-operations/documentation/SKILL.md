---
id: documentation
name: Documentation
description: Write documentation that answers real questions — setup, usage, troubleshooting.
category: 12-operations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [documentation, writing]
compatible_agents: [documentation-agent, ai-engineer]
---

# Documentation

## Purpose
Write docs people actually use: they answer the questions users ask, verify
against the real system, and stay current.

## Principles
1. **Answer real questions** — "how do I install", "how do I configure X",
   "why is this failing". Doc the questions, not the org chart.
2. **Verify everything** — every command and code block is run; every URL is
   real. Untested docs are lies.
3. **Structure for scanning** — titles as questions; one idea per section;
   tables over prose; code first, explanation after.
4. **Right level** — README: 60-second orientation. Docs: task-oriented how-tos.
   Reference: complete and precise. Keep them separate.
5. **Troubleshooting** — symptoms → causes → fixes, from common to rare.
6. **Maintain** — docs are code: versioned, reviewed, updated with changes.

## README structure
What it is → quickstart (real commands) → config → common tasks → how to
contribute/test → troubleshooting → license.

## Rules
- If a command in the docs isn't executed and verified, remove it or mark it
  as unverified.
- Docs that duplicate code comments add noise — delete them.