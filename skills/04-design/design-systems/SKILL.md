---
id: design-systems
name: Design Systems
description: "Design systems as engineering — tokens, components, variants, states, governance — with verification."
category: 04-design
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, repo.tree]
risk_level: low
cost_level: low
dependencies: [ui-design, frontend-engineering]
compatible_agents: [design-systems-engineer, ui-designer, frontend-lead]
tags: [design-systems, tokens, components]
contract:
  prerequisites:
    - "an existing UI to systematize or a greenfield decision"
  preferred_agents: [design-systems-engineer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "token/component inventory from the actual codebase"
  artifact_contract:
    - "design system (tokens, component specs, usage rules, governance)"
  quality_gates:
    - "tokens defined before components that hardcode values"
    - "every component has variants, states, and usage guidance"
    - "governance rules (when to add vs reuse)"
  verification:
    - "search the codebase for hardcoded values that should be tokens"
  failure_modes:
    system_bloat: "cap component count; prefer composition"
    token_proliferation: "merge near-duplicate tokens"
  escalation:
    - "systems whose adoption requires rewrites across the product"
  handoff_in:
    - "existing UI"
    - "product intent"
  handoff_out:
    - "design system spec for implementation"
  evaluation:
    - "token coverage of the actual UI"
    - "governance enforceability"
  observability:
    - "record system decisions and adoption status"
  related_skills: [ui-design, frontend-engineering, visual-hierarchy]
---

# Design Systems

## Purpose
Build design systems as engineering artifacts: token-driven, componentized,
with variants, states and governance rules — verified against the real
codebase.

## When to use / When NOT to use
- use: multi-screen products, team consistency, scaling UI work
- avoid: one-off landing pages (a full system is overkill); avoid a system
  that exists only as documentation nobody uses

## Inputs & assumptions
- inputs: existing UI (or greenfield decision), product intent
- assumptions: adoption scope is assumed unless agreed — record it

## Workflow
1. **Inventory** — extract actual colors, type, spacing, radii from the
   codebase (repo.search/repo.tree).
2. **Tokens** — define semantic tokens (not raw values): color roles,
   type scale, spacing scale, motion durations.
3. **Components** — each with variants, all states (hover, focus, disabled,
   loading, empty, error), and usage guidance.
4. **Governance** — rules: when to extend vs reuse, how to deprecate, review
   cadence.
5. **Verification** — search for hardcoded values that should be tokens;
   check component coverage of real screens.

## Evidence requirements
- Token and component inventory grounded in the actual codebase.

## Artifact contract
- `design-system`: tokens, component specs (variants, states, usage),
  governance rules, migration notes.

## Quality gates (definition of done)
- [ ] Tokens defined before hardcoded components
- [ ] Every component has variants, states, usage guidance
- [ ] Governance rules written and enforceable
- [ ] Hardcoded-value scan done

## Verification
- Search the codebase for hardcoded colors/spacing that bypass tokens.
- Spot-check that key screens compose only system components.

## Failure & recovery
| failure | recovery |
|---|---|
| system bloat | cap components; prefer composition over new components |
| token proliferation | merge near-duplicates; document deprecation |
| unused system | measure adoption; report the gap |

## Escalation
- Adoption requiring cross-product rewrites — escalate the migration scope
  decision.

## Handoff
- receives: existing UI, product intent
- passes: design system spec (tokens, components, governance) to frontend
  engineering

## Evaluation
The org evaluates this skill by token coverage of the real UI and
governance enforceability — documentation alone is not a system.

## Observability
- Record system decisions and adoption status in the project.

## References
- references/patterns.md — token naming and component composition rules