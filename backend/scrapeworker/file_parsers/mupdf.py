import fitz

from backend.scrapeworker.common.utils import deburr
from backend.scrapeworker.file_parsers.base import FileParser


class MuPdfParse(FileParser):
    def __init__(self, *args, **kwargs):
        super(MuPdfParse, self).__init__(*args, **kwargs)
        self.doc = fitz.Document(self.file_path)

    async def get_info(self) -> dict[str, str]:
        return self.doc.metadata

    async def get_text(self):
        pdftext_out = ""
        for page in self.doc:
            text = page.get_text()
            pdftext_out += deburr(text.strip())
        return pdftext_out.strip()

    def get_title(self, metadata):
        title = metadata.get("title") or metadata.get("subject") or str(self.filename_no_ext)
        return title
