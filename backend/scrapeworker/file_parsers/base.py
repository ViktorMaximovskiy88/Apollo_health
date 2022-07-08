import os
import pathlib

from abc import ABC
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.common.detect_lang import detect_lang
from backend.scrapeworker.common.utils import date_rgxs
from backend.scrapeworker.date_parser import DateParser


class FileParser(ABC):

    text: str = ""
    metadata: dict[str, str] = {}
    result: dict[str, str] = {}

    def __init__(
        self,
        file_path: str,
        url: str,
    ):
        self.file_path = file_path
        self.url = url
        self.filename_no_ext = pathlib.Path(os.path.basename(self.url)).with_suffix("")

    async def get_info(self) -> dict[str, str]:
        raise NotImplementedError("get_info is required")

    async def get_text(self) -> str:
        raise NotImplementedError("get_text is required")

    def get_title(self):
        raise NotImplementedError("get_title is required")

    async def parse(self) -> dict[str, str]:
        self.metadata = await self.get_info()
        self.text = await self.get_text()
        title = self.get_title(self.metadata)
        document_type, confidence = classify_doc_type(self.text)
        lang_code = detect_lang(self.text)

        date_parser = DateParser(self.text, date_rgxs)
        date_parser.extract_dates()
        identified_dates = list(date_parser.unclassified_dates)
        identified_dates.sort()

        self.result = {
            "metadata": self.metadata,
            "identified_dates": identified_dates,
            "effective_date": date_parser.effective_date["date"],
            "end_date": date_parser.end_date["date"],
            "last_updated_date": date_parser.last_updated_date["date"],
            "next_review_date": date_parser.next_review_date["date"],
            "next_update_date": date_parser.next_update_date["date"],
            "published_date": date_parser.published_date["date"],
            "title": title,
            "document_type": document_type,
            "confidence": confidence,
            "lang_code": lang_code,
        }

        return self.result
