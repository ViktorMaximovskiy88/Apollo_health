import re
from typing import Any

from aiohttp import ClientResponse
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument
from backend.scrapeworker.common.utils import (
    extension_to_mimetype_map,
    get_extension_from_content_type,
    get_extension_from_file_mime_type,
    get_extension_from_path_like,
)
from backend.scrapeworker.playbook import PlaybookContext


class Metadata(BaseModel):
    link_text: str | None = None
    element_id: str | None = None
    closest_heading: str | None = None
    href: str | None = None
    base_url: str | None = None
    playbook_context: PlaybookContext | None = None


class Request(BaseModel):
    method: str = "GET"
    headers: dict[str, str] = {}
    url: str
    data: Any | None = None
    # TODO move to response ..
    filename: str | None = None


class Response(BaseModel):
    content_type: str | None = None
    content_disposition_filename: str | None = None
    status: int | None = None
    content_length: int | None = None

    def from_aio_response(self, response: ClientResponse):
        headers = response.headers
        self.status = response.status
        self.content_type = self.get_content_type(headers)
        self.content_disposition_filename = self.get_content_disposition_filename(headers)
        self.content_length = headers.get("content-length") or 0

    def get_content_disposition_filename(self, headers) -> str | None:
        matched = None
        if content_disposition := headers.get("content-disposition"):
            matched = re.search('filename="(.*)";', content_disposition)

        if matched:
            return matched.group(1)
        else:
            return None

    def get_content_type(self, headers) -> str | None:
        matched = None
        if content_type := headers.get("content-type"):
            matched = re.search("(^[^;]*)", content_type)

        if matched:
            return matched.group(1)
        else:
            return None


class DownloadContext(BaseModel):
    metadata: Metadata = Metadata()
    request: Request
    response: Response = Response()
    seen_doc: BaseDocument | None = None

    file_name: str | None = None
    file_extension: str | None = None
    file_path: str | None = None
    file_hash: str | None = None
    file_size: int = 0

    alternate_url: str | None = None

    content_hash: str | None = None
    content_type: str | None = None

    def guess_extension(self) -> None:
        guess_ext = get_extension_from_path_like(self.request.url)

        if not guess_ext:
            guess_ext = get_extension_from_path_like(self.response.content_disposition_filename)

        if not guess_ext:
            guess_ext = get_extension_from_content_type(self.response.content_type)

        if not guess_ext:
            guess_ext = get_extension_from_file_mime_type(self.file_path)

        self.file_extension = guess_ext
        self.content_type = extension_to_mimetype_map[guess_ext] or None
