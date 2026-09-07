# Agent OS — the Unified AI Agency / Agent Operating System

A multi-agent platform where you talk to an entire organization of AI agents
through **Mattermost**. Agents collaborate, delegate, spawn sub-agents, use
skills and MCP tools, route work to the right models, respect budgets, ask
for human approval on dangerous actions, and keep full audit trails.

Built as one coherent operating system — not ten repos glued together:
LangGraph orchestration, PostgreSQL + Redis persistence, a pluggable model
router (Claude / DeepSeek / GLM / local / offline echo), a skill registry
with progressive disclosure, an MCP registry, structured agent-to-agent
messaging, an approval system, a CLI, and a web admin UI.

> 🧪 **Works fully offline.** With no API keys set, the built-in `echo`
> provider runs the entire pipeline (demo included) so you can see and test
> everything before adding keys.

---

## Quickstart

```bash
# 1. install
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. run the offline end-to-end demo (no keys needed)
agent-os demo

# 3. start the full system
agent-os start          # API + worker + Mattermost listener
# open the admin UI at http://localhost:8300

# 4. check everything
agent-os health
agent-os status
```

With Docker:

```bash
cp .env.example .env     # add keys
docker compose up --build -d
```

With Mattermost (see [docs/MATTERMOST.md](docs/MATTERMOST.md)): set
`MATTERMOST_URL` + `MATTERMOST_TOKEN`, start the system, and message the bot
in `town-square`:

```
I want to build a new SaaS product.            → executive creates a project
@agent status                                   → live agent status board
@agent approve apr_xxx                          → approve a high-risk action
@agent stop cto / @agent resume cto             → human override
```

---

## What's inside

| Subsystem | Where | Notes |
|---|---|---|
| Control plane API + admin UI | `agentos/api/`, `agentos/admin/` | FastAPI, single-file SPA |
| Orchestration | `agentos/orchestration/` | LangGraph state machine, checkpoints, retries, approval gates |
| Agent runtime | `agentos/agents/` | prompt composition, model loop, tool execution, reflection |
| Agent registry | `agentos/registries/agent_registry.py` | 41 agents in a hierarchical org chart |
| Skill registry | `agentos/registries/skill_registry.py` + `skills/` | 100 skills, 20 branches, progressive loading |
| Model layer | `agentos/models/` | providers (Claude/DeepSeek/GLM/OpenAI-compat/echo), router, failover |
| Budgets | `agentos/budgets/` | global/project/agent/task limits, auto-downgrade |
| Tools + MCP | `agentos/tools/`, `agentos/registries/mcp_registry.py` | least-privilege executor, MCP streamable-HTTP client |
| Memory | `agentos/memory/` | agent/project/org/user/task scopes |
| Messaging | `agentos/messaging/` | structured agent-to-agent messages |
| Projects & tasks | `agentos/projects/`, `agentos/tasks/` | dependency graphs, auto-unblocking |
| Security | `agentos/security/` | permissions, approvals, audit log |
| Mattermost | `agentos/integrations/mattermost/` | identity layer, workspace org, commands |
| CLI | `agentos/cli/main.py` | `agent-os …` |
| Workflows | `workflows/*.yaml` | declarative 0→100, discovery, build-feature |
| Prompts | `prompts/*.md` | versioned, composable role prompts |

## Key commands

```bash
agent-os start | stop | status | health
agent-os agents list | create | disable | enable | show
agent-os skills list | search | enable | disable | reload
agent-os projects list | create | show
agent-os tasks list | create | show | retry
agent-os models list
agent-os budget status
agent-os mcp list | register
agent-os apis list
agent-os workflows list | run
agent-os approvals list | approve | reject
agent-os events | audit | memory
agent-os ask "your goal"      # executive flow
agent-os demo                 # offline end-to-end demo
```

## The 0 → 100 workflow

`agent-os ask "I want to build a SaaS product"` runs:

```
understanding → discovery → community intelligence → opportunity → strategy →
product definition → PRD → design → architecture → implementation → testing →
security → performance → final review → deployment (⚠️ human approval) → monitoring
```

Every stage is executed by the appropriate agent, artifacts land in the
project's sandboxed workspace, and everything is visible in Mattermost, the
admin UI, the event stream and the audit log.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design and data flow
- [INSTALLATION.md](docs/INSTALLATION.md) — local, Docker, and production notes
- [CONFIGURATION.md](docs/CONFIGURATION.md) — every env var explained
- [AGENTS.md](docs/AGENTS.md) — the org chart, permissions, spawning
- [SKILLS.md](docs/SKILLS.md) — skill architecture and progressive disclosure
- [MCP.md](docs/MCP.md) — MCP servers, registry, permissions
- [MODELS.md](docs/MODELS.md) — tiers, routing, failover, cost control
- [MATTERMOST.md](docs/MATTERMOST.md) — wiring the human interface
- [SECURITY.md](docs/SECURITY.md) — permissions, approvals, audit
- [WORKFLOWS.md](docs/WORKFLOWS.md) — declarative workflows and gates
- [OBSERVABILITY.md](docs/OBSERVABILITY.md) — events, logs, budgets
- [ADMIN-UI.md](docs/ADMIN-UI.md) — the web console
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) — extending the system
- [TESTING.md](docs/TESTING.md) — running the test suite
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — common problems

## License

MIT — see [LICENSE](LICENSE). Skills adapted from the approved capability
sources (Superpowers, Addy Osmani code review, MengTo design methodology,
GSAP official docs, Reddit research practices) carry provenance in their
frontmatter.