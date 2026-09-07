"""Bootstrap — composition root and lifecycle.

Wires every subsystem together: services, orchestrator engine, Mattermost
connection + listener, event → Mattermost sink, and the worker loop.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import Any, Optional

from agentos.config import Settings, get_settings
from agentos.integrations.mattermost.client import MattermostClient
from agentos.integrations.mattermost.listener import MattermostListener
from agentos.integrations.mattermost.service import MattermostService
from agentos.orchestration.engine import OrchestratorEngine
from agentos.services import Services

logger = logging.getLogger("agentos")


async def build_app(settings: Optional[Settings] = None) -> Services:
    settings = settings or get_settings()
    svc = Services(settings)
    await svc.init_db()
    await svc.seed()

    # engine
    svc.engine = OrchestratorEngine(svc)
    svc.engine.get_graph()

    # mattermost
    if settings.mattermost_url and settings.mattermost_token:
        client = MattermostClient(settings.mattermost_url, settings.mattermost_token)
        service = MattermostService(settings, client)
        svc.mattermost = service
        service.svc = svc
        if await service.connect():
            await service.ensure_workspace()
            svc.events.subscribe(service.route_event)
            # listen for human messages
            listener = MattermostListener(service)
            service.listener = listener
        else:
            logger.warning("mattermost offline — continuing without it")
    else:
        logger.info("mattermost not configured (set MATTERMOST_URL/MATTERMOST_TOKEN)")

    return svc


async def run_control_plane(svc: Services, stop_event: Optional[asyncio.Event] = None) -> None:
    """Run API + worker + mattermost listener until stopped."""
    stop_event = stop_event or asyncio.Event()
    tasks = []

    # API server
    from agentos.api.main import create_app
    import uvicorn

    app = create_app(svc)
    config = uvicorn.Config(app, host=svc.settings.api_host, port=svc.settings.api_port,
                            log_level="warning")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())
    tasks.append(api_task)

    # worker
    worker_task = asyncio.create_task(svc.engine.worker_loop(stop_event=stop_event))
    tasks.append(worker_task)

    # mattermost listener
    if svc.mattermost is not None and getattr(svc.mattermost, "listener", None):
        tasks.append(asyncio.create_task(svc.mattermost.listener.run(stop_event=stop_event)))

    async def _shutdown() -> None:
        stop_event.set()
        server.should_exit = True

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))
        except NotImplementedError:
            pass

    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        pass
    await svc.close()


async def on_mattermost_command(svc: Services) -> Any:
    """Handler wiring human Mattermost messages into the control plane."""

    async def handler(message: dict) -> None:
        msg_type = message.get("type")
        try:
            if msg_type == "goal":
                result = await svc.engine.execute_goal(message.get("text", ""),
                                                       user_id=message.get("user_id", "human"))
                if svc.mattermost:
                    await svc.mattermost.post_to(
                        "executive",
                        f"🚀 Project `{result['project_id']}` created — "
                        f"workflow run `{result['run_id']}` status: {result['status']}")
            elif msg_type == "approval":
                decision = message.get("decision", "approved")
                await svc.engine.approve(message.get("approval_id", ""), decision,
                                         decided_by=message.get("user_id", "human"))
            elif msg_type == "retry":
                task_id = message.get("task_id", "")
                if task_id:
                    task = await svc.tasks.get(task_id)
                    if task and task.status.value in ("failed", "cancelled"):
                        await svc.tasks.set_status(task_id, task.status)  # touch
                        await svc.queue.enqueue({"task_id": task_id})
        except Exception as exc:  # noqa: BLE001
            logger.exception("command handling failed")
            if svc.mattermost:
                await svc.mattermost.post_to("system-errors", f"Command failed: {exc}")

    return handler