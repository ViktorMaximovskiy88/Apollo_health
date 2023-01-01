import os
import pathlib
from abc import ABC
from typing import Any

import aiofiles

from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.detect_lang import detect_lang
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs, normalize_string
from backend.scrapeworker.doc_type_classifier import guess_doc_type


class FileParser(ABC):

    text: str = ""
    metadata: dict[str, Any] = {}
    result: dict[str, Any] = {}

    def __init__(
        self,
        file_path: str,
        url: str,
        link_text: str | None = None,
        download: DownloadContext | None = None,
        scrape_method_config: ScrapeMethodConfiguration | None = None,
    ):
        self.file_path = file_path
        self.download = download
        self.url = url
        self.link_text = link_text or ""
        file_name = self.url.removesuffix("/")
        self.filename_no_ext = str(pathlib.Path(os.path.basename(file_name)).with_suffix(""))
        self.scrape_method_config = scrape_method_config

    async def get_info(self) -> dict[str, str]:
        raise NotImplementedError("get_info is required")

    async def get_text(self) -> str:
        raise NotImplementedError("get_text is required")

    def get_title(self, _):
        raise NotImplementedError("get_title is required")

    async def read_text_file(self, encoding="utf-8"):
        async with aiofiles.open(
            self.file_path,
            mode="r",
            encoding=encoding,
        ) as file:
            return await file.read()

    async def parse(self) -> dict[str, Any]:
        self.metadata = await self.get_info()
        self.text = await self.get_text()
        title = self.get_title(self.metadata)

        document_type, confidence, doc_vectors, doc_type_match = guess_doc_type(
            self.text, self.link_text, self.url, title, self.scrape_method_config
        )
        lang_code = detect_lang(self.text)

        date_parser = DateParser(date_rgxs, label_rgxs)
        label_texts: list[str] = [text for text in [title, self.link_text] if text is not None]
        date_parser.extract_dates(self.text, label_texts)

        identified_dates = list(date_parser.unclassified_dates)
        identified_dates.sort()

        scrubbed_link_text = normalize_string(self.link_text)
        scrubbed_url = normalize_string(self.url)

        self.result = {
            "metadata": self.metadata,
            "identified_dates": identified_dates,
            "effective_date": date_parser.effective_date.date,
            "end_date": date_parser.end_date.date,
            "last_updated_date": date_parser.last_updated_date.date,
            "last_reviewed_date": date_parser.last_reviewed_date.date,
            "next_review_date": date_parser.next_review_date.date,
            "next_update_date": date_parser.next_update_date.date,
            "published_date": date_parser.published_date.date,
            "title": title,
            "text": self.text,
            "document_type": document_type,
            "confidence": confidence,
            "lang_code": lang_code,
            "doc_vectors": doc_vectors,
            "scrubbed_url": scrubbed_url,
            "scrubbed_link_text": scrubbed_link_text,
            "doc_type_match": doc_type_match,
        }

        return self.result
