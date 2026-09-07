"""Mattermost service + REST API tests."""

import pytest

from agentos.domain.models import AgentDef
from agentos.integrations.mattermost.service import format_identity


class FakeMmClient:
    """Tiny in-memory stand-in for the Mattermost REST client."""

    def __init__(self):
        self.posts = []
        self.channels = {}
        self.team_id = "team1"
        self.bot_id = "bot1"

    async def me(self):
        return {"id": self.bot_id, "username": "agent-os"}

    async def health(self):
        return True

    async def get_team_by_name(self, name):
        return {"id": self.team_id, "name": name}

    async def create_team(self, name, display_name):
        return {"id": self.team_id, "name": name}

    async def get_channel_by_name(self, team_id, name):
        return self.channels.get(name)

    async def create_channel(self, team_id, name, display_name, purpose=""):
        self.channels[name] = {"id": f"ch-{name}"}
        return self.channels[name]

    async def post(self, channel_id, message, root_id=None):
        self.posts.append({"channel_id": channel_id, "message": message, "root_id": root_id})
        return {"id": f"p{len(self.posts)}"}

    async def posts_after(self, channel_id, since):
        return []


def test_identity_formatting():
    agent = AgentDef(id="cto", name="CTO", role="technology")
    assert format_identity(agent, "claude-sonnet-4-5") == "[claude-sonnet-4-5 • CTO]"
    assert format_identity(agent) == "[T2 • CTO]"


@pytest.mark.asyncio
async def test_mattermost_workspace_creation(svc):
    from agentos.config import Settings
    from agentos.integrations.mattermost.service import MattermostService

    settings = Settings(mattermost_url="http://fake", mattermost_token="tok",
                        mattermost_team="ai-agency")
    service = MattermostService(settings, FakeMmClient())
    svc.mattermost = service
    service.svc = svc
    assert await service.connect()
    await service.ensure_workspace()
    for name in ("executive", "approvals", "agent-status", "system-errors"):
        assert name in service.channels


@pytest.mark.asyncio
async def test_mattermost_agent_posting(svc):
    from agentos.config import Settings
    from agentos.integrations.mattermost.service import MattermostService

    client = FakeMmClient()
    service = MattermostService(Settings(mattermost_url="http://fake", mattermost_token="t"),
                                client)
    svc.mattermost = service
    service.svc = svc
    await service.connect()
    await service.ensure_workspace()
    agent = await svc.agent_registry.get("cto")
    await service.post_as_agent(agent, "Architecture completed.", model="claude-sonnet-4-5")
    assert client.posts
    assert "[claude-sonnet-4-5 • CTO]" in client.posts[0]["message"]


@pytest.mark.asyncio
async def test_mattermost_approval_command(svc):
    from agentos.config import Settings
    from agentos.integrations.mattermost.service import MattermostService

    client = FakeMmClient()
    service = MattermostService(Settings(mattermost_url="http://fake", mattermost_token="t"),
                                client)
    svc.mattermost = service
    service.svc = svc
    await service.connect()
    await service.ensure_workspace()

    # create a paused workflow, then approve it from a Mattermost message
    project = await svc.projects.create("MM", "obj", workflow_id="build_feature")
    run = await svc.engine.run_workflow("build_feature", project.project_id)
    pending = await svc.approvals.pending()
    approval_id = pending[0].approval_id

    await service.handle_message({"message": f"@agent approve {approval_id}",
                                  "user_id": "human-1"}, svc.engine, svc)
    refreshed = await svc.approvals.get(approval_id)
    assert refreshed.status.value == "approved"
    # the run resumed to completion
    saved = svc.engine._active_runs[run["run_id"]]["state"]
    assert saved["status"] == "completed"


@pytest.mark.asyncio
async def test_mattermost_goal_message(svc):
    from agentos.config import Settings
    from agentos.integrations.mattermost.service import MattermostService

    client = FakeMmClient()
    service = MattermostService(Settings(mattermost_url="http://fake", mattermost_token="t"),
                                client)
    svc.mattermost = service
    service.svc = svc

    async def on_command(message):
        if message["type"] == "goal":
            await svc.engine.execute_goal(message["text"], user_id=message["user_id"],
                                          workflow_id="discovery")

    service.on_command = on_command
    await service.connect()
    await service.ensure_workspace()
    await service.handle_message({"message": "Build me a booking tool",
                                  "user_id": "human-2"}, svc.engine, svc)
    projects = await svc.projects.list()
    assert len(projects) == 1
    assert "booking" in projects[0].objective.lower()


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_api_endpoints(svc):
    from fastapi.testclient import TestClient

    from agentos.api.main import create_app

    app = create_app(svc)
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        status = client.get("/api/status")
        assert status.status_code == 200
        assert status.json()["agents"]["available"] >= 12

        agents = client.get("/api/agents")
        assert agents.status_code == 200
        assert len(agents.json()) >= 12

        skills = client.get("/api/skills")
        assert skills.status_code == 200
        assert len(skills.json()) >= 50

        models = client.get("/api/models")
        assert models.status_code == 200
        assert any(m["id"] == "echo" for m in models.json())

        # goal via API
        goal = client.post("/api/goals", json={
            "goal": "Validate an idea", "workflow_id": "discovery"})
        assert goal.status_code == 200
        assert goal.json()["status"] == "completed"

        # admin UI serves
        ui = client.get("/")
        assert ui.status_code == 200
        assert "Agent OS" in ui.text