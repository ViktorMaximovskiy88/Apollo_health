import asyncio
from functools import cached_property
from pathlib import Path

from spacy.tokens.span import Span

from backend.common.core.enums import SectionType
from backend.common.core.utils import now
from backend.common.models.doc_document import DocDocument, TherapyTag
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import FocusSectionConfig
from backend.scrapeworker.document_tagging.base_tagger import BaseTagger
from backend.scrapeworker.document_tagging.tag_focusing import FocusChecker

SPECIAL_CHARACTERS = ["\u00AE", "\u2122", "\24C7", "\u2020", "\u271D"]


class TherapyTagger(BaseTagger):
    section_type = SectionType.THERAPY
    model_key = "rxnorm-span"

    @cached_property
    def common_words(self):
        common_words_path = Path(__file__).parent.joinpath("common_words.txt")
        return {line.strip() for line in open(common_words_path)}

    def clean_page(self, page: str):
        for symbol in SPECIAL_CHARACTERS:
            page = page.replace(symbol, " ")
        return page

    async def tag_document(
        self,
        full_text: str,
        doc_type: str,
        url: str,
        link_text: str | None,
        focus_configs: list[FocusSectionConfig] | None = None,
        document: RetrievedDocument | DocDocument | None = None,
    ) -> tuple[list[TherapyTag], list[TherapyTag], list[TherapyTag]]:
        nlp = await self.model()
        if not nlp:
            return ([], [], [])
        if focus_configs is not None:
            focus_configs = self._filter_focus_configs(focus_configs, doc_type)
            focus_checker = FocusChecker(full_text, focus_configs, url, link_text, doc_type)
        elif document:
            focus_checker = await FocusChecker.with_all_location_configs(
                document, SectionType.THERAPY, full_text, url, link_text
            )
        else:
            return ([], [], [])

        tags: set[TherapyTag] = set()
        url_tags = set()
        link_tags = set()
        pages = full_text.split("\f")
        loop = asyncio.get_running_loop()
        char_offset = 0
        for i, page in enumerate(pages):
            page = self.clean_page(page)
            doc = await loop.run_in_executor(None, nlp, page)
            span: Span
            for span in doc.spans.get("sc", []):
                text = span.text
                if text.lower() in self.common_words:
                    continue

                focus_state = focus_checker.check_focus(span, offset=char_offset)
                lexeme = span.vocab[span.label]
                splits = lexeme.text.split("|")
                rxcui, drugid, display_name, priority = "", "", "", 0
                if len(splits) == 2:
                    drugid, display_name = splits
                elif len(splits) == 3:
                    drugid, rxcui, display_name = splits
                if ":" in drugid:
                    drugid, priority_str = drugid.split(":")
                    priority = int(priority_str)
                if not rxcui:
                    rxcui = None

                if focus_state.is_in_link_text or focus_state.is_in_url:
                    context_tag = TherapyTag(
                        text=text.lower(),
                        code=drugid,
                        rxcui=rxcui,
                        name=display_name,
                        page=-1,
                        focus=focus_state.focus,
                        priority=priority,
                        created_at=now(),
                    )

                    if focus_state.is_in_link_text:
                        link_tags.add(context_tag)
                    if focus_state.is_in_url:
                        url_tags.add(context_tag)

                tag = TherapyTag(
                    text=text,
                    code=drugid,
                    rxcui=rxcui,
                    name=display_name,
                    page=i,
                    focus=focus_state.focus,
                    key=focus_state.key,
                    priority=priority,
                    text_area=focus_state.section,
                    created_at=now(),
                )
                tags.add(tag)
            char_offset += len(page) + 1

        return list(tags), list(url_tags), list(link_tags)


therapy_tagger = TherapyTagger()
