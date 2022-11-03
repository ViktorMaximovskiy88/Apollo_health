import json

import boto3


class SqsClient:
    def __init__(self, queue_name: str, endpoint_url: str) -> None:
        self.queue_name = queue_name
        self.sqs = boto3.resource("sqs", endpoint_url=endpoint_url)
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)

    def send(self, message: dict[str, any]):
        body = json.dumps(message)
        response = self.queue.send_message(MessageBody=body)
        return response

    def send_batch(self, messages: list[dict[str, any]]):
        entries = [
            {"Id": str(index), "MessageBody": json.dumps(message)}
            for index, message in enumerate(messages)
        ]
        response = self.queue.send_messages(Entries=entries)
        return response
