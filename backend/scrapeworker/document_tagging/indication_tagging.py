import asyncio

import spacy
from spacy.tokens import Span

from backend.common.core.enums import SectionType
from backend.common.models.doc_document import IndicationTag
from backend.common.models.indication import Indication
from backend.common.models.site import FocusSectionConfig
from backend.scrapeworker.document_tagging.tag_focusing import FocusChecker


class IndicationTagger:
    def __init__(self) -> None:
        self.terms: dict[str, list[Indication]] = {}
        self.nlp = None
        self.lock = asyncio.Lock()

    async def model(self):
        if not self.nlp:
            async with self.lock:
                self.nlp = spacy.blank("en")
                # saw a value of 20074378... bumping more
                self.nlp.max_length = 300000000
                ruler = self.nlp.add_pipe(
                    "span_ruler", config={"spans_key": "sc", "phrase_matcher_attr": "LOWER"}
                )
                async for indication in Indication.find():
                    for term in indication.terms:
                        ruler.add_patterns(  # type: ignore
                            [
                                {
                                    "label": f"{term}|{indication.indication_number}",
                                    "pattern": term,
                                }
                            ]
                        )
        return self.nlp

    def __get_focus_configs(self, configs: list[FocusSectionConfig], doc_type: str):
        filtered = [
            config
            for config in configs
            if config.doc_type == doc_type and (SectionType.INDICATION in config.section_type)
        ]
        return filtered

    async def tag_document(
        self,
        text: str,
        doc_type: str,
        url: str,
        link_text: str | None,
        focus_configs: list[FocusSectionConfig],
    ) -> list[IndicationTag]:
        nlp = await self.model()
        if not nlp:
            return []

        tags = set()
        focus_configs = self.__get_focus_configs(focus_configs, doc_type)
        focus_checker = FocusChecker(text, focus_configs, url, link_text)
        pages = text.split("\f")
        loop = asyncio.get_running_loop()
        char_offset = 0
        for i, page in enumerate(pages):
            doc = await loop.run_in_executor(None, nlp, page)
            spans: list[Span] = doc.spans.get("sc", [])
            for span in spans:
                focus_state = focus_checker.check_focus(span, offset=char_offset)
                text = span.text
                lexeme = span.vocab[span.label]
                term, indication_number = lexeme.text.split("|")
                tag = IndicationTag(
                    text=term,
                    page=i,
                    code=int(indication_number),
                    focus=focus_state.focus,
                    key=focus_state.key,
                    text_area=focus_state.section,
                )
                tags.add(tag)
            char_offset += len(page) + 1

        return list(tags)


indication_tagger = IndicationTagger()
