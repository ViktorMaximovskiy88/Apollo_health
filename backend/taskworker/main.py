import sys
from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

from backend.app.core.settings import settings
from backend.common.db.init import init_db
from backend.common.sqs.task_queue import TaskQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task")


async def main():
    await init_db()
    logger.info("Starting the task queue worker")

    queue = TaskQueue(
        queue_url=settings.task_worker_queue_url,
        logger=logger,
    )

    await queue.listen()


if __name__ == "__main__":
    asyncio.run(main())
