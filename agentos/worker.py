"""Standalone worker process.

Consumes the task queue and runs tasks. Used by the Docker worker service
and available locally via `python -m agentos.worker`.
"""

from __future__ import annotations

import asyncio
import logging

from agentos.bootstrap import build_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("agentos.worker")


async def main() -> None:
    svc = await build_app()
    logger.info("worker online (queue: %s)", type(svc.queue).__name__)
    await svc.engine.worker_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("worker stopped")