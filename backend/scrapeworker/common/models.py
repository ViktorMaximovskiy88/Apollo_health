from typing import Any
from pydantic import BaseModel, AnyHttpUrl

class Metadata(BaseModel):
    text: str

class Request(BaseModel):
    method: str = "GET"
    headers: dict[str, str] | None
    url: AnyHttpUrl
    body: dict[str, Any] | None

class Download(BaseModel):
    metadata: Metadata 
    request: Request
