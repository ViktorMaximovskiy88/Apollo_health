import sys
from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

from backend.common.db.init import init_db
from backend.common.sqs.pdf_diff_task import PDFDiffTaskQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdfdiff")


async def main():
    await init_db()
    logger.info("Starting the pdf queue worker")

    queue = PDFDiffTaskQueue(
        queue_name="pdf-diff-queue.fifo",
        endpoint_url="http://localhost:9324",
        logger=logger,
    )

    await queue.listen()


if __name__ == "__main__":
    asyncio.run(main())
