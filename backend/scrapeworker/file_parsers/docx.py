import docx2txt
from docx import Document
from backend.scrapeworker.file_parsers.base import FileParser


class DocxParser(FileParser):
    async def get_text(self) -> str:
        text = docx2txt.process(self.file_path)
        return text

    async def get_info(self) -> dict[str, str]:
        doc = Document(self.file_path)
        return {
            "title": doc.core_properties.title,
            "category": doc.core_properties.category,
            "subject": doc.core_properties.subject,
        }

    def get_title(self, metadata) -> str | None:
        title = (
            metadata["title"]
            or metadata["subject"]
            or metadata["category"]
            or str(self.filename_no_ext)
        )
        return title
