import logging

import boto3

from backend.common.core.config import config, is_local
from backend.common.events.settings import settings


class SendEventClient:
    def __init__(self):

        self.source = settings.event_source
        self.event_bus_name = settings.event_bus_name
        if is_local:
            self.client = boto3.client(
                "events",
                region_name=config["AWS_REGION"],
                aws_access_key_id=config["EB_AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=config["EB_AWS_SECRET_ACCESS_KEY"],
            )
        else:
            self.client = boto3.client("events")

    def send_event(self, detail_type, message_body):
        logging.info(
            f"Will send {detail_type} event with {self.source} source to {self.event_bus_name} event bus"  # noqa
        )
        response = self.client.put_events(
            Entries=[
                {
                    "Source": self.source,
                    "DetailType": detail_type,
                    "Detail": message_body,
                    "EventBusName": self.event_bus_name,
                }
            ]
        )
        logging.info(f"Event Send Response: {response}")
        return response
