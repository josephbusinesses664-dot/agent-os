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