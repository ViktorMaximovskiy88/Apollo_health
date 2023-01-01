import json
import logging
from abc import ABC
from urllib.parse import urlparse

import boto3


class SQSBase(ABC):
    def __init__(
        self,
        queue_url: str,
        max_number_of_messages: int = 1,
        wait_time_seconds: int = 1,
        logger=logging,
    ) -> None:
        self.logger = logger
        # local vs aws parsing, mreh
        self.parse_queue_url(queue_url)
        self.sqs = boto3.resource(
            "sqs",
            endpoint_url=self.endpoint_url,
        )
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)
        self.logger.info(f"{self.queue_name} initialized for endpoint {self.endpoint_url}")
        self.max_number_of_messages = max_number_of_messages
        self.wait_time_seconds = wait_time_seconds

    # sets both queuename and endpoint url
    def parse_queue_url(self, queue_url):
        parsed_url = urlparse(queue_url)
        paths = parsed_url.path.split("/")
        self.queue_name = paths.pop()
        self.endpoint_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.endpoint_url += "/".join(paths)

    # JSON encode message and send it
    def send(self, message: dict[str, any], group_id: str):
        body = json.dumps(message, default=str)
        deduplication_id = message.get("id", None)  # None string is ok
        response = self.queue.send_message(
            MessageBody=body,
            MessageDeduplicationId=str(deduplication_id),
            MessageGroupId=group_id,
        )
        return response

    def receive(self):
        messages = self.queue.receive_messages(
            MaxNumberOfMessages=self.max_number_of_messages,
            WaitTimeSeconds=self.wait_time_seconds,
        )
        return [(message, json.loads(message.body)) for message in messages]

    # JSON encode multiple messages and send them
    def send_batch(self, messages: list[dict[str, any]], group_id: str | None = None):
        entries = [
            {
                "Id": str(index),
                "MessageBody": json.dumps(message, default=str),
                "MessageDeduplicationId": str(message.get("id", None)),
                "MessageGroupId": group_id,
            }
            for index, message in enumerate(messages)
        ]
        response = self.queue.send_messages(Entries=entries)
        return response
