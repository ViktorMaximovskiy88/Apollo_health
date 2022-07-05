from typing import Any
from pydantic import BaseModel, AnyHttpUrl


class Metadata(BaseModel):
    link_text: str | None
    element_id: str | None
    closest_heading: str | None
    href: str | None


class Request(BaseModel):
    method: str = "GET"
    headers: Any | None
    url: str
    data: Any | None
    filename: str


class Download(BaseModel):
    metadata: Metadata | None
    request: Request
