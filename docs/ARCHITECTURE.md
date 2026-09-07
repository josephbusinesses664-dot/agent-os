# Architecture

## System map

```
YOU
  ↓  (Mattermost / CLI / Admin UI / REST API)
CONTROL PLANE  (FastAPI + CLI + worker)
  ↓
ORCHESTRATOR  (LangGraph state machine — checkpoints, retries, approval gates)
  ↓
AGENT REGISTRY ─ SKILL REGISTRY ─ TOOL/MCP REGISTRY ─ MODEL ROUTER
  ↓
SPECIALIZED AGENTS  (instantiated per task, never permanently running)
  ↓
EXECUTION → VERIFICATION → RESULTS / MEMORY / AUDIT LOG
```

## Principles

1. **Clean separation** — interface, control plane, orchestration, agents,
   skills, tools, models, memory, projects, security, observability and
   configuration are separate layers. Every major component is replaceable
   (see the registry pattern below).
2. **Pluggability over coupling** — new models, skills, agents, MCP servers,
   APIs and workflows are added through registries and YAML/prompt files,
   never by editing core code.
3. **Agents are definitions, not processes** — the registry holds 41 agent
   definitions; the orchestrator instantiates one only for the duration of a
   task, then returns it to idle.
4. **Progressive disclosure** — skills are indexed with metadata; a task
   triggers a search and only the top-k relevant skill bodies enter model
   context. The system can hold thousands of skills without bloating every
   request.
5. **Truthful state over impressive UI** — agents never claim actions without
   evidence (tool results, test output, deployment reports). The echo provider
   explicitly labels its output as offline simulation.
6. **Resilience** — no single provider or service is load-bearing. Model
   failover chains, graceful degradation when Mattermost/DB/Redis are down,
   and in-memory fallbacks keep the system functional offline.

## Key flows

### Workflow execution
`run_workflow(workflow_id, project_id)` → LangGraph `step` node loops over the
workflow's stages. Each stage:

1. creates a task assigned to the stage's agent role,
2. instantiates the agent runtime (prompt = role prompt + project context +
   relevant memory + loaded skills + permitted tools + constraints),
3. routes a model (complexity + budget + availability),
4. runs the model/tool loop (deduplicated tool calls, permission checks,
   approval gates for high-risk tools),
5. records usage/cost, artifacts, events and audit entries,
6. emits `stage.completed`; the graph routes to the next stage, a retry
   (transient failures with backoff), a human-approval pause, or completion.

Runs are checkpointed per `run_id` (LangGraph checkpointer), so a paused or
interrupted run resumes from saved state.

### Delegation / spawning
An agent that needs help requests a sub-agent task. The engine enforces hard
limits: max recursion depth, max parallel agents, budget checks, and
duplicate-task detection. Depth `executive → cto → frontend-lead → ui-engineer`
works; `agent → 10 → 100 → 10,000 agents` is structurally impossible.

### Human approval
Stages marked `requires_approval` (e.g. deployment) execute their work, pause
the run at `awaiting_approval`, and post an approval request (Mattermost +
admin UI + CLI). A human approves/rejects via `@agent approve <id>`,
`agent-os approvals approve <id>`, or the admin UI; the run resumes from its
checkpoint. High-risk *tools* (e.g. `shell`) are gated the same way.

## Storage

- **Repository** — document store (`collection, key → JSON`). In-memory
  implementation for tests/offline; PostgreSQL implementation (JSONB) for
  deployment. Every subsystem persists through the same interface.
- **KV + Queue** — Redis when configured; in-memory fallback otherwise. Used
  for the task queue, counters and caching.
- **Memory** — durable entries at agent/project/org/user/task scope with
  keyword/tag recall; vector search is added only where it demonstrably helps.
- **Audit** — append-only log of every significant action
  (who/what/when/why/project/task/tool/model/result).

## Module layout

```
agentos/
├── api/            REST control plane + admin UI
├── agents/         definitions (hierarchy) + runtime
├── budgets/        budget manager
├── cli/            agent-os CLI
├── db/             repository + kv/queue abstractions (memory/postgres/redis)
├── domain/         canonical pydantic models
├── integrations/   mattermost, mcp, apis
├── memory/         multi-scope memory store
├── messaging/      structured agent-to-agent bus
├── models/         providers + router
├── observability/  event bus + health checks
├── orchestration/  LangGraph state machine + engine
├── projects/       project lifecycle
├── prompts/        versioned role prompts
├── registries/     agents, skills, tools, mcp, apis, models
├── security/       permissions, approvals, audit
├── services.py     composition root
└── tasks/          task lifecycle + dependency graph
skills/             20 branches of SKILL.md capabilities
workflows/          declarative workflow YAML
prompts/            versioned prompts (source of truth)
config/             documented defaults
docker/             container build + worker entrypoint
tests/              unit / integration / workflow / e2e / security
```