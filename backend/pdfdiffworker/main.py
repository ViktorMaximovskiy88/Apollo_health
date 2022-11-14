import sys
from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

from backend.app.core.settings import settings
from backend.common.db.init import init_db
from backend.common.sqs.pdfdiff_task_queue import PDFDiffTaskQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdfdiff")


async def main():
    await init_db()
    logger.info("Starting the pdfdiff queue worker")

    queue = PDFDiffTaskQueue(
        queue_url=settings.pdfdiff_worker_queue_url,
        logger=logger,
    )

    await queue.listen()


if __name__ == "__main__":
    asyncio.run(main())
