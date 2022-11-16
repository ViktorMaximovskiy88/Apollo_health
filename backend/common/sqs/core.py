import json
import logging
from abc import ABC
from urllib.parse import urlparse

import boto3

from backend.common.core.config import config


class SQSBase(ABC):
    def __init__(self, queue_url: str, logger=logging) -> None:
        self.logger = logger
        # local vs aws parsing, mreh
        self.parse_queue_url(queue_url)
        self.sqs = boto3.resource(
            "sqs",
            endpoint_url=self.endpoint_url,
            region_name=config["AWS_REGION"],
        )
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)
        self.logger.info(f"{self.queue_name} initialized for endpoint {self.endpoint_url}")

    # sets both queuename and endpoint url
    def parse_queue_url(self, queue_url):
        parsed_url = urlparse(queue_url)
        paths = parsed_url.path.split("/")
        self.queue_name = paths.pop()
        self.endpoint_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.endpoint_url += "/".join(paths)


class SQSListener(SQSBase):
    def __init__(
        self,
        queue_url: str,
        logger=logging,
        max_number_of_messages=1,
        wait_time_seconds=1,
    ) -> None:
        super().__init__(queue_url, logger)
        self.max_number_of_messages = max_number_of_messages
        self.wait_time_seconds = wait_time_seconds

    async def listen(self):
        while True:
            messages = self.queue.receive_messages(
                MaxNumberOfMessages=self.max_number_of_messages,
                WaitTimeSeconds=self.wait_time_seconds,
            )
            for message in messages:
                try:
                    parsed_body = json.loads(message.body)
                    await self.process_message(
                        message,
                        parsed_body,
                    )
                except Exception as e:
                    await self.handle_exception(e, message, parsed_body)
                    continue
                message.delete()

    async def process_message(self, message: dict, body: dict):
        pass

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        pass


class SQSClient(SQSBase):
    # JSON encode message and send it
    def send(self, message: dict[str, any], group_id: str):
        # JSON encode message and send it
        body = json.dumps(message, default=str)
        deduplication_id = message.get("id", None)  # None string is ok
        response = self.queue.send_message(
            MessageBody=body,
            MessageDeduplicationId=str(deduplication_id),
            MessageGroupId=group_id,
        )
        return response

    # JSON encode multiple messages and send them
    def send_batch(self, messages: list[dict[str, any]]):
        entries = [
            {"Id": str(index), "MessageBody": json.dumps(message, default=str)}
            for index, message in enumerate(messages)
        ]
        response = self.queue.send_messages(Entries=entries)
        return response
