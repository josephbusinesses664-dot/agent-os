---
id: technical-research
name: Technical Research
description: "Docs-grounded technical research — official sources first, version-verified, with executable verification where possible."
category: 10-research
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape, shell.write]
risk_level: low
cost_level: low
dependencies: [research-planning, evidence-synthesis]
compatible_agents: [technical-researcher, ai-engineer]
tags: [research, technical, documentation]
contract:
  prerequisites:
    - "the technical question and its decision context"
  preferred_agents: [technical-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "claims grounded in official docs where available"
    - "version numbers recorded for API/library claims"
  artifact_contract:
    - "technical research (answer, evidence, version notes, verification)"
  quality_gates:
    - "official sources preferred over SEO spam"
    - "version-verified claims"
    - "executable verification where feasible (code run, not assumed)"
  verification:
    - "run a minimal reproduction when the claim is code"
  failure_modes:
    memory_docs: "verify against current docs — libraries change"
    stale_version: "record the version the claim applies to"
  escalation:
    - "contradictions between docs and observed behavior"
  handoff_in:
    - "question"
    - "context"
  handoff_out:
    - "technical research with evidence and verification"
  evaluation:
    - "source quality"
    - "version accuracy"
    - "executable verification"
  observability:
    - "record sources and versions"
  related_skills: [evidence-synthesis, tech-decision, api-evaluation]
---

# Technical Research

## Purpose
Answer technical questions from evidence: official docs first, version
numbers recorded, and executable verification where the claim is code.

## When to use / When NOT to use
- use: library/API questions, architecture feasibility, debugging unknowns
- avoid: answering from memory when docs exist — verify

## Inputs & assumptions
- inputs: question, decision context
- assumptions: every claim's applicable version recorded

## Workflow
1. Restate the question and the decision it serves.
2. Search official docs, then reputable secondary sources.
3. Record version numbers for every API/library claim.
4. Where the claim is code, run a minimal reproduction (shell.write).
5. Synthesize with confidence; flag doc-vs-behavior contradictions.

## Evidence requirements
- Official sources preferred; SEO spam deprioritized.
- Versions recorded; executable verification where feasible.

## Artifact contract
- `technical-research`: answer, evidence (source, version), verification
  results, confidence.

## Quality gates (definition of done)
- [ ] Official sources preferred
- [ ] Version-verified claims
- [ ] Executable verification where feasible
- [ ] Contradictions flagged

## Verification
- Run the minimal reproduction when the claim is code.

## Failure & recovery
| failure | recovery |
|---|---|
| memory docs | verify against current docs |
| stale version | record the applicable version |
| doc-behavior conflict | reproduce, then escalate |

## Escalation
- Contradictions between docs and observed behavior.

## Handoff
- receives: question, context
- passes: technical research with evidence and verification

## Evaluation
The org evaluates this skill by source quality, version accuracy, and
executable verification.

## Observability
- Record sources and versions in the audit trail.

## References
- references/patterns.md — doc-verification workflow