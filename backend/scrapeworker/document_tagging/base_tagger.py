import tempfile
from abc import ABC

import spacy

from backend.common.core.enums import SectionType
from backend.common.models.app_config import AppConfig
from backend.common.models.site import FocusSectionConfig
from backend.common.storage.client import ModelStorageClient


class BaseTagger(ABC):
    section_type: SectionType
    model_key: str

    def __init__(self) -> None:
        self.nlp = None
        self.version = None

    def _filter_focus_configs(self, configs: list[FocusSectionConfig], doc_type: str):
        filtered = [
            config
            for config in configs
            if config.doc_type == doc_type and (self.section_type in config.section_type)
        ]
        return filtered

    async def get_version(self):
        config = await AppConfig.find_one({"key": "model_versions"})
        if config:
            return config.data[self.model_key]
        return "latest"

    async def model(self):
        latest_version = await self.get_version()
        if latest_version == self.version and self.nlp:
            return self.nlp

        try:
            self.client = ModelStorageClient()
            self.tempdir = tempfile.TemporaryDirectory()
            dirname = self.tempdir.name
            self.client.download_directory(f"{latest_version}/{self.model_key}", dirname)
            self.nlp = spacy.load(dirname)
            self.nlp.max_length = 300_000_000
            self.version = latest_version
        except Exception:
            print(f"{self.model_key} Model not found and therefore not loaded")
            self.nlp = None

        return self.nlp
