from importlib.metadata import metadata
import logging

import io
import re
from typing import BinaryIO, TextIO, Optional
import pathlib

import attr
import bs4
import magic
from backend.app.utils.logger import Logger
import os

from backend.scrapeworker.xpdf_wrapper import pdfinfo, pdftotext

# logger = logging.getLogger(__name__)


class UnknownFileTypeError(Exception):
    pass


@attr.s(auto_attribs=True)
class TextExtractor:
    document_bytes: bytes = attr.ib(repr=False)
    mimetype: Optional[str]
    full_text: str = attr.ib(default='')
    word_count: int = attr.ib(default=0)
    page_count: int = attr.ib(default=0)
    temp_path: str = attr.ib(default='')
    metadata: any = attr.ib(default=None)
 
    
    async def extract(self):
        self.get_mimetype()
        self.full_text = await self._extract_text()
        self.word_count = self._calculate_word_count()

    def select_title(self, url):
        filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
        if (self.metadata is None):
            return str(filename_no_ext)
        title = self.metadata.get("Title") or self.metadata.get("Subject") or str(filename_no_ext)
        return title

    def get_mimetype(self):
        if not self.mimetype:
            logging.debug("No mimetype provided at init, inferring...")
            self.mimetype = magic.from_buffer(self.document_bytes, mime=True)
            logging.debug("Inferred mimetype: {0}".format(self.mimetype))

    async def _extract_text(self) -> str:
        """ Extracts text from document based on document type.
            Sets page_count as well.
        """
        if self.mimetype == 'application/pdf':
            self.full_text, self.page_count, self.metadata = \
                await extract_apollo_pdf_text_and_page_count(self.temp_path)

        elif self.mimetype == 'text/html':
            self.full_text = extract_html_text(self.document_bytes)
            self.page_count = 1
        else:
            raise UnknownFileTypeError("No implemented logic for extracting "
                                       "text from mimetype {0}!"
                                       .format(self.mimetype))
        return self.full_text

    def _calculate_word_count(self) -> str:
        """ Calculates word count from document based on full_text.
        """
        if self.full_text == '':
            self._extract_text()
        self.word_count = len(re.sub(' +', ' ', self.full_text).split(' '))
        return self.word_count


async def extract_apollo_pdf_text_and_page_count(temp_path) -> str:    
    pdf = await pdftotext(temp_path)
    metadata = await pdfinfo(temp_path)
    return pdf, len(pdf), metadata

    
def extract_pdf_pages_and_page_count(document_bytes: bytes) -> str:
    f = _get_fileobj_from_bytes(document_bytes)
    pdf = pdftotext.PDF(f)
    Logger.debug("Extracted {0} pages from pdf"
                 .format(len(pdf)))
    return list(pdf), len(pdf)


def _get_fileobj_from_bytes(b: bytes) -> BinaryIO:
    f = io.BytesIO()
    f.write(b)
    f.seek(0)
    return f


def extract_html_text(document_bytes: bytes) -> str:
    """ Tag removal found here: https://stackoverflow.com/a/19760007 """
    f = _get_html_fileobj_from_bytes(document_bytes)
    soup = bs4.BeautifulSoup(f, features="html.parser")
    [s.extract() for s in soup(
        ['style', 'script', '[document]',
         'head', 'title'])]
    return soup.getText()


def _get_html_fileobj_from_bytes(b: bytes) -> TextIO:
    # TODO add chardet to properly decode data
    f = io.StringIO()
    f.write(b.decode('utf-8'))
    f.seek(0)
    return f
