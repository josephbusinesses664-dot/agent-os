"""Shared fixtures: everything runs against the in-memory backend."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

os.environ.setdefault("AGENTOS_LOG_LEVEL", "WARNING")


@pytest.fixture
async def svc(tmp_path):
    """A fully seeded Services bundle (in-memory storage, echo provider)."""
    from agentos.config import Settings
    from agentos.orchestration.engine import OrchestratorEngine
    from agentos.services import Services

    settings = Settings(
        database_url=None,
        redis_url=None,
        workspace_dir=str(tmp_path / "workspace"),
        log_level="WARNING",
    )
    services = Services(settings)
    await services.seed()
    services.engine = OrchestratorEngine(services)
    services.engine.get_graph()
    yield services
    await services.close()


@pytest.fixture
def tmp_workspace(tmp_path) -> Path:
    return tmp_path / "workspace"