import os
import signal
import sys
from pathlib import Path
from uuid import uuid4

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

from backend.app.core.settings import settings
from backend.common.db.init import init_db
from backend.common.tasks.task_queue import TaskQueue

worker_id = str(uuid4())
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(worker_id)
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
        await queue.listen(worker_id)
    except (KeyboardInterrupt, SystemExit):
        await queue.onshutdown()
        sys.exit(0)


if __name__ == "__main__":
    logger.info(f"PID: {os.getpid()}")
    asyncio.run(main())
