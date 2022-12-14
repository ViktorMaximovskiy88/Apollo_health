import os
import signal
import sys
from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

from backend.app.core.settings import settings
from backend.common.db.init import init_db
from backend.common.tasks.task_queue import TaskQueue

logging.basicConfig()
logger = logging.getLogger("task")
logger.setLevel(logging.INFO)


queue = TaskQueue(
    queue_url=settings.task_worker_queue_url,
    logger=logger,
)


def shutdown(signum, frame):
    raise SystemExit


signal.signal(signal.SIGTERM, shutdown)


async def main():
    try:
        await init_db()
        logger.info("Starting the task queue worker")
        await queue.listen()
    except (KeyboardInterrupt, SystemExit):
        await queue.onshutdown()
        sys.exit(0)


if __name__ == "__main__":
    logger.info(f"PID: {os.getpid()}")
    asyncio.run(main())
