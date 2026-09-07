# Testing

The suite runs fully offline (in-memory storage + echo provider). No API
keys, no Docker services required.

```bash
pytest                 # everything
pytest -q              # quiet
pytest tests/test_workflow.py   # one module
pytest -m integration   # integration tests (MCP always; Postgres/Redis env-gated)
```

## Coverage by area

| File | Covers |
|---|---|
| `test_domain.py` | models, permissions, cost math |
| `test_registries.py` | agent CRUD, org hierarchy, skill search ranking, progressive loading, categories, tools, models, APIs, MCP |
| `test_budget_router.py` | approve/downgrade/reject, scoped tracking, day rollover, tier routing, failover |
| `test_tasks_memory_messaging.py` | dependency unblocking, memory scoping, structured messages, decisions |
| `test_security.py` | permission denial, high-risk tool approval gate, audit trail, path escapes |
| `test_workflow.py` | completion, approval pause/resume, rejection, retries, checkpoints, spawn limits, goals |
| `test_agents_runtime.py` | tool loop, dedupe, honest offline markers, worker paths |
| `test_mattermost_api.py` | identity formatting, workspace creation, commands, goal handling, REST endpoints |
| `test_integration.py` | MCP client against a real local JSON-RPC server; Postgres/Redis (env-gated) |
| `test_e2e.py` | full 0→100 pipeline, failure recovery keeps project state |

## Coverage by area

- `test_memory.py` — multi-entry storage, TF-IDF semantic recall, versioned
  facts, fact extraction, episodes, consolidation
- `test_capabilities.py` — executable skills (inline code sandbox, skill
  tools, validators, repo.search / db.query / file.patch)
- `test_tools_upgrade.py` — capability discovery, permission scopes,
  strategy-change retries, timeouts, secret redaction, tool/MCP health,
  tool spans
- `test_performance.py` — stats recording, leaderboard, router + delegation
  influence
- `test_evaluation.py` — deterministic evaluator, judge fallback, benchmark
  run, cost-aware leaderboards, failure categorization
- `test_collaboration.py` — handoffs/blockers, escalation on subagent
  failure, delegation depth/duplicate limits, inbox context
- `test_trace.py` — span chains (agent → model → tool)
- `test_autonomy.py` — the full agency loop end-to-end (plan → research →
  design → implement → verify → review → report) plus transient-failure
  recovery
- `test_memory_r3.py` — knowledge-graph links, contradiction resolution,
  temporal validity, evolution-vs-contradiction, provenance chains
- `test_planning.py` — dynamic stage selection (minimal vs full pipeline),
  `PLANNED_STAGES` marker, template-built workflows, engine execution
- `test_browser.py` — real Playwright browser automation (open/snapshot/
  click/type) against local pages, through the executor + permission system
  (skipped when Playwright is not installed)
- `test_mcp_auth_adapters.py` — MCP credential isolation/redaction,
  read-only GitHub/Postgres/Docker adapters (technically enforced),
  adapter least-privilege
- `test_failure_analysis.py` — failure categories, recommendations,
  best-match selection from evaluation history (cost/latency aware)
- `test_integration_r3.py` — the round-3 integration test: memory + dynamic
  capability selection + tool discovery + delegation + evaluation +
  performance routing, all in one loop

## Integration env vars

```bash
export AGENTOS_TEST_DATABASE_URL=postgresql+asyncpg://…   # enables Postgres tests
export AGENTOS_TEST_REDIS_URL=redis://…                    # enables Redis tests
```

## Rules

- Evidence over claims: tests execute real code paths and assert on real
  outputs (artifacts on disk, event streams, audit entries, task states).
- No sleeps for timing; conditions are awaited.
- A bug fix ships with a failing-then-passing regression test.