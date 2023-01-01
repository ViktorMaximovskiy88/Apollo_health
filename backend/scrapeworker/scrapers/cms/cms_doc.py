import json
import os
import tempfile
from enum import Enum
from typing import Any


class CmsDocType(Enum):
    NCD = 1
    LCD = 2
    LCA = 3


class CmsDoc:
    def __init__(self, type: CmsDocType) -> None:
        self.type = type

    @classmethod
    def from_url(cls, url: str) -> "CmsDoc":
        if "article-details" in url or "article-list" in url:
            return cls(CmsDocType.LCA)
        elif "lcd-details" in url or "lcd-list" in url:
            return cls(CmsDocType.LCD)
        elif "ncd-details" in url or "ncd-alphabetical-index" in url:
            return cls(CmsDocType.NCD)
        raise ReferenceError("Url does not match a known doc type")

    def local_path(self) -> str:
        """
        Retrieve a local temp directory name
        :return: Temp directory for specific document type
        """
        return f"{tempfile.gettempdir()}/{self.type.name}"

    def download_url(self):
        """
        Retrieve a path for downloading specific dataset
        :return: Dataset download URL
        """
        base_url = "https://downloads.cms.gov/medicare-coverage-database/downloads/exports/"
        if self.type == CmsDocType.LCA:
            return f"{base_url}current_article.zip"
        elif self.type == CmsDocType.LCD:
            return f"{base_url}current_lcd.zip"
        elif self.type == CmsDocType.NCD:
            return f"{base_url}ncd.zip"

    def inner_archive_name(self):
        inner_archive_names = {
            CmsDocType.NCD: "ncd_csv.zip",
            CmsDocType.LCD: "current_lcd_csv.zip",
            CmsDocType.LCA: "current_article_csv.zip",
        }
        return inner_archive_names[self.type]

    def document_mapping(self) -> dict[str, Any]:
        current_path = os.path.dirname(os.path.realpath(__file__))
        file_path = f"{current_path}/templates/{self.type.name}/mapping.json"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Mapping file: "{file_path}" was not found.')
        with open(file_path, "r") as f:
            json_mapping: dict[str, Any] = json.load(f)
        return json_mapping

    def html_template(self) -> str:
        current_path = os.path.dirname(os.path.realpath(__file__))
        file_path = f"{current_path}/templates/{self.type.name}/index.html"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Template file: "{file_path}" was not found.')
        with open(file_path, "r") as f:
            return f.read()
