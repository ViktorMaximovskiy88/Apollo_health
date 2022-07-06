import os
import magic
from backend.scrapeworker.file_types import docx, xlsx, pdf

__all__ = ["docx", "xlsx", "pdf"]

# TODO ... not as accurate as id like...
# mapper = mimetypes.MimeTypes().types_map_inv
mapper = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/pdf": "pdf",
}


def guess_extension(file_path: str):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mapper[mime_type]


async def parse_by_type(file_path: str, url):
    file_extension = guess_extension(file_path)

    if file_extension == "pdf":
        return await pdf.parse_metadata(file_path, url)
    elif file_extension == "docx":
        return await docx.parse_metadata(file_path, url)
    elif file_extension == "xlsx":
        return await xlsx.parse_metadata(file_path, url)
    else:
        raise NotImplementedError(f"no parse for file ext {file_extension}")
