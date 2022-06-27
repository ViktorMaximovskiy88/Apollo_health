from typing import Any
from pydantic import BaseModel, AnyHttpUrl

class Metadata(BaseModel):
    text: str

class Request(BaseModel):
    method: str = "GET"
    headers: Any | None
    url: str
    body: Any | None

class Download(BaseModel):
    metadata: Metadata 
    request: Request
