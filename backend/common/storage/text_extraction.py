import logging

import bs4
import magic

from backend.scrapeworker.common.xpdf_wrapper import pdfinfo, pdftotext


class UnknownFileTypeError(Exception):
    pass


class TextExtractor:
    def __init__(self, document_bytes, mimetype="", temp_path=""):
        self.document_bytes = document_bytes
        self.mimetype = mimetype
        self.temp_path = temp_path

    async def extract(self):
        self.get_mimetype()
        self.full_text = await self._extract_text()

    def title_from_metadata(self):

        if not self.metadata:
            return None
        return self.metadata.get("Title") or self.metadata.get("Subject")

    def get_mimetype(self):
        if not self.mimetype:
            logging.debug("No mimetype provided at init, inferring...")
            self.mimetype = magic.from_buffer(self.document_bytes, mime=True)
            logging.debug("Inferred mimetype: {0}".format(self.mimetype))

    async def _extract_text(self) -> str:
        """Extracts text from document based on document type.
        Sets page_count as well.
        """
        if self.mimetype == "application/pdf":
            if not self.temp_path:
                raise UnknownFileTypeError(
                    "Extracting text from {0} requires temp_path!".format(self.mimetype)
                )
            self.full_text, self.metadata = await extract_pdf_text(self.temp_path)

        elif self.mimetype == "text/html":
            self.full_text = extract_html_text(self.document_bytes)
            self.page_count = 1
        else:
            raise UnknownFileTypeError(
                "No implemented logic for extracting "
                "text from mimetype {0}!".format(self.mimetype)
            )
        return self.full_text


async def extract_pdf_text(temp_path) -> tuple[str, dict[str, str]]:
    pdf = await pdftotext(temp_path)
    metadata = await pdfinfo(temp_path)
    return pdf, metadata


def extract_html_text(document_bytes: bytes) -> str:
    """Tag removal found here: https://stackoverflow.com/a/19760007"""
    soup = bs4.BeautifulSoup(document_bytes, features="html.parser")
    [s.extract() for s in soup(["style", "script", "[document]", "head", "title"])]
    return soup.getText()
