from typing import Any
from pydantic import BaseModel, AnyHttpUrl

class Metadata(BaseModel):
    text: str 
    id: str | None

class Request(BaseModel):
    method: str = "GET"
    headers: Any | None
    url: str
    data: Any | None

class Download(BaseModel):
    metadata: Metadata 
    request: Request
