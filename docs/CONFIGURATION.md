# Configuration

All configuration is environment-based (`.env` file or exported vars).
Secrets are never stored in code or committed. `.env.example` documents every
variable; this page explains the important ones.

## Persistence

| Var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | *(empty → in-memory)* | `postgresql+asyncpg://user:pass@host:5432/db`. Persistent store for all aggregates. |
| `REDIS_URL` | *(empty → in-memory)* | `redis://host:6379/0`. Task queue, counters, cache. |
| `WORKSPACE_DIR` | `./workspace` | Sandboxed file area for agents; path escapes are blocked and every write is audit-logged. |

## Mattermost

| Var | Purpose |
|---|---|
| `MATTERMOST_URL` | Base URL of the Mattermost server. |
| `MATTERMOST_TOKEN` | Personal access token of the bot account (System Console → Personal Access Tokens). |
| `MATTERMOST_TEAM` | Team the bot manages (`ai-agency` by default; created if missing). |
| `MATTERMOST_POLL_INTERVAL` | Listener polling interval in seconds. |
| `ADMIN_USER_IDS` | Comma-separated Mattermost user ids granted override power. |

## Model providers

| Var | Purpose |
|---|---|
| `DEFAULT_PROVIDER` | `echo` (offline) by default. When keys are present, routing considers all configured providers. |
| `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` | DeepSeek (OpenAI-compatible). |
| `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` | Claude. |
| `GLM_API_KEY` / `GLM_BASE_URL` | GLM (OpenAI-compatible). |
| `OPENAI_COMPAT_API_KEY` / `OPENAI_COMPAT_BASE_URL` | Any OpenAI-compatible endpoint (Ollama, vLLM, etc.). |

Models are defined in `agentos/registries/model_registry.py` (tier, price,
fallbacks) and can be added/re-tiered there or via the registry.

## Budgets (USD)

`GLOBAL_BUDGET_MONTHLY`, `GLOBAL_BUDGET_DAILY`, `DEFAULT_PROJECT_BUDGET`,
`AUTO_DOWNGRADE_ON_BUDGET`. Before an expensive call the router estimates
cost, checks global/project/agent/task limits, and either approves, downgrades
to a cheaper tier, or rejects.

## Agent limits

`MAX_AGENT_DEPTH` (spawn recursion), `MAX_PARALLEL_AGENTS`,
`MAX_TASK_RETRIES` (transient failures), `MAX_TASK_SECONDS`.

## Security

`REQUIRE_APPROVAL_RISK=high` — tools/stages at or above this risk require
human approval. See [SECURITY.md](SECURITY.md).

## Operations

`LOG_LEVEL`, `API_HOST`, `API_PORT`, `WORKER_POLL_INTERVAL`.

## Where defaults live

`agentos/config.py` (Settings) is the source of truth; `config/defaults.yaml`
documents the intended defaults; env vars always win.