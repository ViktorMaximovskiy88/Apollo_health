from typing import List

from aws_lambda_powertools.utilities.parser import BaseModel, envelopes, event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import AnyUrl, BaseSettings


# TODO move...
class Settings(BaseSettings):
    env_type: str

    mongo_url: AnyUrl
    mongo_db: str
    mongo_user: str | None = None
    mongo_password: str | None = None

    task_worker_queue_url: str


class Test(BaseModel):
    message: str


settings = Settings()


@event_parser(model=Test, envelope=envelopes.SqsEnvelope)
def handler(event: List[Test], context: LambdaContext):
    print(event)
    for record in event:
        print(record)
