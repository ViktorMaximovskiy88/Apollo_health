import sys
from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

import boto3

from backend.common.db.init import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf_diff_task")

queue_name = "pdf-diff-queue"


async def main():
    await init_db()
    logger.info("Starting the pdf queue worker")

    sqs = boto3.resource(
        "sqs",
        region_name="local",
        aws_access_key_id="none",
        aws_secret_access_key="none",
        endpoint_url="http://localhost:9324",
    )
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    while True:
        messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=1)
        for message in messages:
            try:
                print(message.body)
            except Exception as e:
                logger.error(f"Exception while processing message: {repr(e)}", exc_info=1)
                continue
            message.delete()


if __name__ == "__main__":
    asyncio.run(main())
