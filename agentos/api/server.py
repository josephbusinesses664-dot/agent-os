"""uvicorn entry point: `uvicorn agentos.api.server:app`.

Builds the full service stack at startup (lifespan) and exposes it on
`app.state.svc`. Routes resolve services through the holder in api.main.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from agentos.api.main import create_app, svc_holder
from agentos.bootstrap import build_app
from agentos.config import get_settings

logger = logging.getLogger("agentos")


@asynccontextmanager
async def lifespan(app):
    svc = await build_app(get_settings())
    svc_holder["svc"] = svc
    app.state.svc = svc
    worker = asyncio.create_task(svc.engine.worker_loop())
    app.state.worker_task = worker
    logger.info("control plane ready on :%s", svc.settings.api_port)
    yield
    worker.cancel()
    await svc.close()


app = create_app(None)
app.router.lifespan_context = lifespan