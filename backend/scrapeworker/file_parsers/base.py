import os
import pathlib

from abc import ABC
from typing import Any
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.common.detect_lang import detect_lang
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.document_tagging.taggers import Taggers


class FileParser(ABC):

    text: str = ""
    metadata: dict[str, Any] = {}
    result: dict[str, Any] = {}

    def __init__(
        self,
        file_path: str,
        url: str,
        taggers: Taggers | None = None,
    ):
        self.file_path = file_path
        self.url = url
        self.taggers = taggers
        self.filename_no_ext = pathlib.Path(os.path.basename(self.url)).with_suffix("")

    async def get_info(self) -> dict[str, str]:
        raise NotImplementedError("get_info is required")

    async def get_text(self) -> str:
        raise NotImplementedError("get_text is required")

    def get_title(self, _):
        raise NotImplementedError("get_title is required")

    async def parse(self) -> dict[str, Any]:
        self.metadata = await self.get_info()
        self.text = await self.get_text()
        title = self.get_title(self.metadata)
        document_type, confidence = classify_doc_type(self.text)
        lang_code = detect_lang(self.text)

        date_parser = DateParser(self.text, date_rgxs, label_rgxs)
        date_parser.extract_dates()
        identified_dates = list(date_parser.unclassified_dates)
        identified_dates.sort()

        therapy_tags, indication_tags = [], []
        if self.taggers:
            therapy_tags = await self.taggers.therapy.tag_document(self.text)
            indication_tags = await self.taggers.indication.tag_document(self.text)

        self.result = {
            "metadata": self.metadata,
            "identified_dates": identified_dates,
            "effective_date": date_parser.effective_date["date"],
            "end_date": date_parser.end_date["date"],
            "last_updated_date": date_parser.last_updated_date["date"],
            "last_reviewed_date": date_parser.last_reviewed_date["date"],
            "next_review_date": date_parser.next_review_date["date"],
            "next_update_date": date_parser.next_update_date["date"],
            "published_date": date_parser.published_date["date"],
            "title": title,
            "text": self.text,
            "document_type": document_type,
            "confidence": confidence,
            "lang_code": lang_code,
            "therapy_tags": therapy_tags,
            "indication_tags": indication_tags,
        }

        return self.result
