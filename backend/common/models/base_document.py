from datetime import datetime

from beanie import Document
from pydantic import BaseModel

json_encoders = {datetime: lambda dt: dt.isoformat(timespec="milliseconds") + "Z"}


class BaseDocument(Document):
    def created(self) -> datetime:
        if not self.id:
            return datetime.utcfromtimestamp(0)
        return self.id.generation_time

    class Config:
        json_encoders = json_encoders


class BaseModel(BaseModel):
    class Config:
        json_encoders = json_encoders
