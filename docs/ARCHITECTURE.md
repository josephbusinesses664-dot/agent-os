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
7. **Operational incentives** — performance statistics (success rate, cost,
   latency, tool efficiency, review scores) are *used*: weaker agents get
   routed to stronger models, proven ones earn cheaper tiers, delegation
   prefers the best track record. No cosmetic XP.
8. **One implementation per responsibility** — memory, evaluation and
   observability each have a single canonical store; new ideas are integrated
   behind those interfaces rather than added as parallel systems.

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

### Agent run loop (observe → plan → act → verify → recover)
`runtime.run()` composes the prompt (role + project context + semantic memory
recall + relevant skills + permitted tools + **inbox messages from the
parent**), routes a model, and runs the model/tool loop with deduplicated
calls. After the loop it **verifies** deterministically (claimed artifacts
must exist on disk; failed tool calls are accounted for — no evidence, no
"verified"), records a reflection, and `_post_run`:

1. extracts durable facts (marked Decision:/Lesson:/Preference:/Fact:) and
   the task episode into memory with provenance,
2. sends a structured `task_result`/`failure` to the parent agent,
3. folds the outcome into the agent's performance stats.

### Capabilities (executable skills)
A skill is not only a prompt: frontmatter can attach executable tools
(built-in handler refs or sandboxed inline python), pre/post hooks,
validators, model settings, permissions, examples and tests. The
`CapabilityManager` binds skill tools into the ToolRegistry so they flow
through the *same* executor (permission checks, approvals, timeouts,
telemetry) as built-ins. Inline code runs in a restricted namespace — no
`open`/`eval`/`import` — so untrusted skill code cannot touch the host.
See `skills/07-security/secret-scanning` for a worked example (executable
scanner + redaction validator).

### Memory
One store, five layers (task/project/agent/org/user). Recall is TF-IDF
semantic ranking blended with importance and recency — deterministic and
offline. Facts are versioned (a restated fact supersedes the old one with a
`supersedes` link, never a silent overwrite); completed tasks become
retrievable episodes; consolidation archives stale low-access entries and
merges duplicates. Every entry carries provenance
(`agent:<id> task:<id>`).

### Evaluation & performance
Every stage/task outcome is scored by the deterministic evaluator (evidence
checklist) and optionally an LLM judge; records persist and feed the
`PerformanceTracker`. The model router reads performance (`influence()`)
and delegation picks children by track record (`engine.pick_child`).
`eval_sets/*.jsonl` are regression datasets; `agent-os evaluate basic` runs a
benchmark through the real engine path and produces cost-aware leaderboards
(`agent-os leaderboard`).

### Tracing
Every meaningful action records a span (kind: agent/stage/model/tool/
evaluator) into the trace store, linked by `trace_id` (task) and
`parent_span`. A task trace is the replayable chain
agent → stage → model → tool → result. `/api/traces/<task_id>` and
`agent-os traces <task_id>` expose it; `trace.span` events stream to
subscribers.

## Storage

- **Repository** — document store (`collection, key → JSON`). In-memory
  implementation for tests/offline; PostgreSQL implementation (JSONB) for
  deployment. Every subsystem persists through the same interface.
- **KV + Queue** — Redis when configured; in-memory fallback otherwise. Used
  for the task queue, counters and caching.
- **Memory** — durable entries at agent/project/org/user/task scope with
  TF-IDF semantic recall; vector search can be layered behind the same
  interface only where it demonstrably helps.
- **Traces** — span store for telemetry (tokens, cost, latency, errors).
- **Evaluation** — evaluation records + benchmark run summaries.
- **Performance** — per-agent rolling statistics (all/weekly/daily).
- **Audit** — append-only log of every significant action
  (who/what/when/why/project/task/tool/model/result).

## Module layout

```
agentos/
├── api/            REST control plane + admin UI
├── agents/         definitions (hierarchy) + runtime (verify/recover loop)
├── budgets/        budget manager
├── capabilities/   capability manager (executable skills, hooks, validators)
├── cli/            agent-os CLI
├── db/             repository + kv/queue abstractions (memory/postgres/redis)
├── domain/         canonical pydantic models
├── evaluation/     deterministic + LLM-judge evaluators, datasets, runner
├── integrations/   mattermost, mcp, apis
├── memory/         layered memory store (semantic recall, versioned facts)
├── messaging/      structured agent-to-agent bus (handoffs, escalation)
├── models/         providers + router (performance-aware)
├── observability/  event bus + tracer + health checks
├── orchestration/  LangGraph state machine + engine
├── performance.py  operational agent stats
├── projects/       project lifecycle
├── prompts/        versioned role prompts
├── registries/     agents, skills, tools, mcp, apis, models
├── security/       permissions, scopes, approvals, audit
├── services.py     composition root
└── tasks/          task lifecycle + dependency graph
skills/             20 branches of SKILL.md capabilities (executable tools)
eval_sets/          regression datasets (JSONL)
workflows/          declarative workflow YAML (incl. agency-loop)
prompts/            versioned prompts (source of truth)
config/             documented defaults
docker/             container build + worker entrypoint
tests/              unit / integration / workflow / e2e / security / autonomy
```