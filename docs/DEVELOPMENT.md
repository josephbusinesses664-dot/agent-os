# Development

## Layout

See [ARCHITECTURE.md](ARCHITECTURE.md) for the module map and design
principles.

## Extending

| To add… | Do this |
|---|---|
| A model | `ModelDef` in `agentos/registries/model_registry.py` (or register via code); provider from `agentos/models/provider.py` if a new protocol is needed. |
| A skill | Drop `skills/<branch>/<id>/SKILL.md` with frontmatter; `agent-os skills reload`. |
| An agent | `AgentDef` via `agentos/agents/hierarchy.py` or `agent-os agents create`; optional prompt at `prompts/<id>.md`. |
| A tool | `ToolDef` + handler in `agentos/tools/builtin.py` or `tool_registry.register(…)`; permission key + risk level mandatory. |
| An MCP server | `McpServer` via registry/CLI/API. |
| An API | `ApiDef` in the catalog; keys via `api_registry.set_key`. |
| A workflow | `workflows/<name>.yaml` (stages reference existing agent roles). |
| A prompt | `prompts/<role>.md` (Jinja2; variables documented in `prompt_library.py`). |

## Conventions

- Type-safe, modular, documented; no giant monolith files.
- Errors are classified (transient/configuration/provider/permission/logic)
  and recoverable where possible — never swallowed.
- New features ship with tests (see [TESTING.md](TESTING.md)).
- Secrets never enter code, configs, or logs.

## Running the pieces

```bash
agent-os start                 # full stack (API + worker + Mattermost)
python -m agentos.worker       # standalone worker
uvicorn agentos.api.server:app --port 8300   # API only
python -m agentos.cli.main status            # any CLI command
```

## Testing

```bash
pytest                          # unit + workflow + e2e + security (in-memory)
pytest -m integration           # Postgres/Redis/MCP (env-gated)
```

The whole suite runs offline with the echo provider — no keys required.