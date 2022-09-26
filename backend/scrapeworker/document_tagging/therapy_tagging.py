import asyncio
import tempfile
from dataclasses import dataclass

import spacy
from spacy.tokens.span import Span

from backend.common.models.doc_document import TherapyTag
from backend.common.models.site import FocusTherapyConfig
from backend.common.storage.client import ModelStorageClient


@dataclass
class FocusArea:
    start: int
    end: int


class FocusChecker:
    def __init__(
        self,
        full_text: str,
        focus_configs: list[FocusTherapyConfig],
        url: str,
        link_text: str | None,
    ) -> None:
        self.full_text = full_text
        self.focus_configs = focus_configs
        self.url = url
        self.link_text = link_text
        self.all_focus = self.check_all_focus()
        self.focus_areas = self.get_focus_areas()

    def check_all_focus(self):
        for config in self.focus_configs:
            if config.all_focus is True:
                return True

        return False

    def get_focus_areas(self) -> list[FocusArea]:
        text_lower = self.full_text.lower()
        focus_areas = []
        for config in self.focus_configs:
            last_match = 0
            start = 0
            while True:
                if not config.start_separator:
                    match = 0
                else:
                    match = text_lower.find(config.start_separator.lower(), last_match)
                if match > -1:
                    if config.start_separator:
                        start = match + len(config.start_separator or "")
                    end = len(self.full_text) - 1
                    if config.end_separator:
                        end_match = text_lower.find(config.end_separator.lower(), start)
                        end = end_match if end_match > -1 else end
                    focus_areas.append(FocusArea(start=start, end=end))
                    last_match = end
                    if not config.start_separator:
                        break
                else:
                    break
        return focus_areas

    def check_focus(self, span: Span, offset: int) -> bool:
        text = span.text.lower()
        if self.all_focus:
            return True
        if self.link_text:
            if text in self.link_text.lower():
                return True
        elif text in self.url.lower():
            return True

        start_char = span.start_char + offset
        end_char = span.end_char + offset
        for focus_area in self.focus_areas:
            if start_char >= focus_area.start and end_char < focus_area.end:
                return True
        return False


class TherapyTagger:
    def __init__(self) -> None:
        self.nlp = None
        try:
            self.client = ModelStorageClient()
            self.tempdir = tempfile.TemporaryDirectory()
            dirname = self.tempdir.name
            self.client.download_directory("rxnorm-span/latest", dirname)
            self.nlp = spacy.load(dirname)
            # This limit assumes the default large NER model is being used
            # We are not using this model so safe to bump limit
            # saw a value of 20074378... bumping more
            self.nlp.max_length = 300000000
        except Exception:
            print("RxNorm Span Ruler Model not found and therefore not loaded")

    async def tag_document(
        self,
        full_text: str,
        doc_type: str,
        url: str,
        link_text: str | None,
        focus_configs: list[FocusTherapyConfig],
    ) -> list[TherapyTag]:
        if not self.nlp:
            return []

        tags: set[TherapyTag] = set()
        focus_configs = [config for config in focus_configs if config.doc_type == doc_type]
        focus_checker = FocusChecker(full_text, focus_configs, url, link_text)
        pages = full_text.split("\f")
        loop = asyncio.get_running_loop()
        char_offset = 0
        for i, page in enumerate(pages):
            doc = await loop.run_in_executor(None, self.nlp, page)
            span: Span
            for span in doc.spans.get("sc", []):
                is_focus = focus_checker.check_focus(span, offset=char_offset)
                text = span.text
                lexeme = span.vocab[span.label]
                splits = lexeme.text.split("|")
                rxcui, drugid, display_name = "", "", ""
                if len(splits) == 2:
                    drugid, display_name = splits
                elif len(splits) == 3:
                    drugid, rxcui, display_name = splits
                if not rxcui:
                    rxcui = None
                tag = TherapyTag(
                    text=text, code=drugid, rxcui=rxcui, name=display_name, page=i, focus=is_focus
                )
                tags.add(tag)
            char_offset += len(page) + 1

        return list(tags)


therapy_tagger = TherapyTagger()
