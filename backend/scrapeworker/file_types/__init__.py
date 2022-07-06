import pathlib
from backend.scrapeworker.file_types import docx, xlsx, pdf

__all__ = ["docx", "xlsx", "pdf"]


async def parse_by_type(file_path: str, url):
    # TODO file ext from content header ...
    file_extension = pathlib.Path(file_path).suffix
    if file_extension == "pdf":
        return await pdf.parse_metadata(file_path, url)
    elif file_extension == "docx":
        return await docx.parse_metadata(file_path, url)
    elif file_extension == "xlsx":
        return await xlsx.parse_metadata(file_path, url)
    else:
        raise NotImplementedError(f"no parse for file ext {file_extension}")
