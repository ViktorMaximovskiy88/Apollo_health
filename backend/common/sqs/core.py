import json
import logging
from abc import ABC

import boto3


class SQSBase(ABC):
    def __init__(self, queue_name: str, endpoint_url: str, logger=logging) -> None:
        self.logger = logger
        self.queue_name = queue_name
        self.sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)
        self.logger.info(f"{self.queue_name} initialized for endpoint {endpoint_url}")


class SQSListener(SQSBase):
    def __init__(
        self,
        queue_name: str,
        endpoint_url: str,
        logger=logging,
        max_number_of_messages=1,
        wait_time_seconds=1,
    ) -> None:
        super().__init__(queue_name, endpoint_url, logger)
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
                    await self.process_message(parsed_body, message=message)
                except Exception as e:
                    await self.handle_exception(e, message, parsed_body)
                    continue
                message.delete()

    async def process_message(self, body: dict, message: dict):
        pass

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        pass


class SQSClient(SQSBase):
    # JSON encode message and send it
    def send(self, message: dict[str, any], dedupe_id: str):
        # JSON encode message and send it
        body = json.dumps(message, default=str)
        response = self.queue.send_message(
            MessageBody=body,
            MessageDeduplicationId=dedupe_id,
            MessageGroupId=dedupe_id,
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
