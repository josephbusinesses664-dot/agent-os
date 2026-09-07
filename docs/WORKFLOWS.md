# Workflows

Workflows are declarative YAML files under `workflows/`. A workflow is a list
of stages; each stage names the agent role that runs it, its dependencies,
and whether it requires human approval. The LangGraph engine executes any
loaded workflow — a new workflow is a YAML file, not a code change.

## Built-in workflows

### zero_to_hundred (`workflows/zero_to_hundred.yaml`)
The reusable 0 → 100 project pipeline:

```
understanding → discovery → community_intelligence → opportunity → strategy →
product_definition → prd → design → architecture → implementation → testing →
security → performance → final_review → deployment (⚠️ approval) → monitoring
```

Modular by design: start at a later `entry_stage` for projects that skip
earlier phases.

### discovery
Research-only: `understanding → discovery → community_intelligence →
opportunity → decision`.

### build_feature
Product → engineering → QA: `requirements → design → implementation →
testing → review → deploy (⚠️ approval)`.

## Stage definition

```yaml
- stage_id: prd
  name: PRD
  agent_role: product-manager        # agent registry id
  description: >                     # becomes the task description
    Write the PRD …
  requires_approval: false           # true → run pauses for human approval
  depends_on: [product_definition]   # ordering metadata
  artifact_prefix: prd
```

`next` is inferred from declaration order; dependencies gate execution.

## Quality gates

Stages are chained so important gates happen at the right points: research
evidence is reviewed before strategy, architecture is approved before
implementation, tests/security/performance must pass before final review, and
deployment requires human approval. Gates are binary and evidence-based —
"tests pass" means the run output exists.

## Running

```bash
agent-os workflows list
agent-os workflows run zero_to_hundred --goal "…" --project <id>
agent-os ask "I want to build a SaaS product"
```

## Adding a workflow

1. Create `workflows/my-flow.yaml` with `workflow_id`, `entry_stage` and
   `stages` (agent roles must exist in the agent registry).
2. `agent-os start` (or restart) loads it; `agent-os workflows list` shows it.
3. Run it with `agent-os workflows run my-flow …`.