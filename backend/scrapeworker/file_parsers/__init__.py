from backend.scrapeworker.file_parsers import docx, xlsx, pdf
from backend.scrapeworker.common.models import Download
from backend.scrapeworker.document_tagging.taggers import Taggers

__all__ = ["docx", "xlsx", "pdf"]


async def parse_by_type(file_path: str, download: Download, taggers: Taggers):
    # TODO use content_type
    file_extension = download.file_extension
    url = download.request.url

    if file_extension == "pdf":
        return await pdf.PdfParse(file_path, url, taggers).parse()
    elif file_extension == "docx":
        return await docx.DocxParser(file_path, url, taggers).parse()
    elif file_extension == "xlsx":
        return await xlsx.XlsxParser(file_path, url, taggers).parse()
    else:
        # raise NotImplementedError(f"no parse for file ext {file_extension}")
        return None
