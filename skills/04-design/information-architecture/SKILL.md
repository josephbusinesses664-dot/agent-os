---
id: information-architecture
name: Information Architecture
description: Organize and label content by user mental models so things are findable.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [ia, navigation, structure]
compatible_agents: [ux-designer, product-manager, documentation-agent]
---

# Information Architecture

## Purpose
Structure content and navigation so users find what they need without
thinking about it.

## Method
1. **Content inventory** — everything that exists; group by user task.
2. **Card sort / mental model** — how do users naturally group items?
   (When you can't test, use their vocabulary and job steps.)
3. **Navigation design** — ≤ 5-7 top-level items; global nav consistent;
   breadcrumbs for deep hierarchies.
4. **Labels** — user language, not org chart language; no cute names for
   critical functions.
5. **Search** — for large systems: searchable + browsable; synonyms mapped.
6. **Wayfinding** — every page answers: where am I, where can I go.

## Rules
- Organize for *finding*, not for the org structure that built the content.
- Ambiguity in labels = failed IA. Test findability on a fresh user.
- Progressive disclosure: more advanced destinations live deeper, not hidden
  in plain sight.