import asyncio
import tempfile
from dataclasses import dataclass
from functools import cached_property, lru_cache
from hashlib import md5
from itertools import pairwise

import spacy
from spacy.tokens.span import Span

from backend.common.models.doc_document import TherapyTag
from backend.common.models.site import FocusTherapyConfig
from backend.common.storage.client import ModelStorageClient


@dataclass
class FocusArea:
    start: int = 0
    end: int = 0


@dataclass
class DocSection:
    start: int = 0
    end: int = 0
    focus: FocusArea = FocusArea()


class FocusChecker:
    def __init__(
        self,
        full_text: str,
        focus_configs: list[FocusTherapyConfig],
        url: str,
        link_text: str | None,
    ) -> None:
        self.full_text = full_text
        self.text_end = len(full_text) - 1
        self.focus_configs = focus_configs
        self.url = url
        self.link_text = link_text

    @cached_property
    def all_focus(self):
        for config in self.focus_configs:
            if config.all_focus is True:
                return True

        return False

    @cached_property
    def sections(self) -> list[DocSection]:
        sections: list[DocSection] = []
        for f1, f2 in pairwise(self.focus_areas):
            sections.append(DocSection(start=f1.start, end=f2.start - 1, focus=f1))
        text_end = len(self.full_text) - 1
        last_focus = self.focus_areas[-1]
        sections.append(DocSection(start=last_focus.start, end=text_end, focus=last_focus))
        return sections

    @cached_property
    def focus_areas(self) -> list[FocusArea]:
        text_lower = self.full_text.lower()
        focus_areas: list[FocusArea] = []
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

    @lru_cache(maxsize=10)
    def section_hash(self, start: int = 0, end: int = 0) -> str:
        if end == 0:
            end = self.text_end

        return md5(self.full_text[start:end].encode()).hexdigest()

    def check_focus(self, span: Span, offset: int) -> tuple[bool, str]:
        text = span.text.lower()
        if self.all_focus:
            return True, self.section_hash()

        if self.link_text:
            if text in self.link_text.lower():
                return True, self.section_hash()
        elif text in self.url.lower():
            return True, self.section_hash()

        start_char = span.start_char + offset
        end_char = span.end_char + offset
        for section in self.sections:
            if start_char >= section.start and end_char < section.end:
                focus_area = section.focus
                if start_char >= focus_area.start and end_char < focus_area.end:
                    return True, self.section_hash(section.start, section.end)
                return False, self.section_hash(section.start, section.end)

        return False, self.section_hash(0, self.focus_areas[0].start)


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
                is_focus, section = focus_checker.check_focus(span, offset=char_offset)
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
                    text=text,
                    code=drugid,
                    rxcui=rxcui,
                    name=display_name,
                    page=i,
                    focus=is_focus,
                    section=section,
                )
                tags.add(tag)
            char_offset += len(page) + 1

        return list(tags)


therapy_tagger = TherapyTagger()
