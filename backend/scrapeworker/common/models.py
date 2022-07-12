import os
import re
import pathlib
import magic

from typing import Any
from pydantic import BaseModel

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

    def from_headers(self, headers):
        self.content_type = self.get_content_type(headers)
        self.content_disposition_filename = self.get_content_disposition_filename(
            headers
        )

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


class Download(BaseModel):
    metadata: Metadata = Metadata()
    request: Request
    response: Response = Response()
    # TODO 'artifact' 'output' or is it indeed just the 'download' ...
    file_name: str | None = None
    file_extension: str | None = None
    file_path: str | None = None
    file_hash: str | None = None
    content_hash: str | None = None

    def guess_extension(self) -> str | None:
        guess_ext = get_extension_from_path_like(self.request.url)

        if not guess_ext:
            guess_ext = get_extension_from_path_like(
                self.response.content_disposition_filename
            )
        if not guess_ext:
            guess_ext = get_extension_from_content_type(self.response.content_type)

        if not guess_ext:
            guess_ext = get_extension_from_file(self.file_path)

        self.file_extension = guess_ext


#  TODO move all of this....
mapper = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/pdf": "pdf",
    "text/html": "html",
}


def get_extension_from_path_like(path_like: str | None) -> str | None:
    if path_like is None:
        return None

    maybe_extension = pathlib.Path(os.path.basename(path_like))
    return maybe_extension.suffix[1:] if maybe_extension else None


def get_extension_from_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None

    return mapper.get(content_type) or None


def get_extension_from_file(file_path: str | None):
    if file_path is None:
        return None

    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mapper.get(mime_type) or None
