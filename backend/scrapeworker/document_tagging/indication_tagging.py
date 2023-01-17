import asyncio

from spacy.tokens import Span

from backend.common.core.enums import SectionType
from backend.common.core.utils import now
from backend.common.models.doc_document import DocDocument, IndicationTag
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import FocusSectionConfig
from backend.scrapeworker.document_tagging.base_tagger import BaseTagger
from backend.scrapeworker.document_tagging.tag_focusing import FocusChecker


class IndicationTagger(BaseTagger):
    model_key = "indication"
    section_type = SectionType.INDICATION

    async def tag_document(
        self,
        text: str,
        doc_type: str,
        url: str,
        link_text: str | None,
        focus_configs: list[FocusSectionConfig] | None = None,
        document: RetrievedDocument | DocDocument | None = None,
    ) -> tuple[list[IndicationTag], list[IndicationTag], list[IndicationTag]]:
        nlp = await self.model()
        if not nlp:
            return ([], [], [])
        focus_checker: FocusChecker
        if focus_configs:
            focus_configs = self._filter_focus_configs(focus_configs, doc_type)
            focus_checker = FocusChecker(text, focus_configs, url, link_text, doc_type)
        elif document:
            focus_checker = await FocusChecker.with_all_location_configs(
                document, SectionType.INDICATION, text, url, link_text
            )
        else:
            return ([], [], [])

        tags = set()
        url_tags = set()
        link_tags = set()
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
                term, name, indication_number = lexeme.text.split("|")

                if focus_state.is_in_link_text or focus_state.is_in_url:
                    context_tag = IndicationTag(
                        name=name,
                        text=term,
                        page=-1,
                        code=int(indication_number),
                        focus=focus_state.focus,
                        created_at=now(),
                    )
                    if focus_state.is_in_link_text:
                        link_tags.add(context_tag)
                    if focus_state.is_in_url:
                        url_tags.add(context_tag)

                tag = IndicationTag(
                    name=name,
                    text=term,
                    page=i,
                    code=int(indication_number),
                    focus=focus_state.focus,
                    key=focus_state.key,
                    text_area=focus_state.section,
                    created_at=now(),
                )
                tags.add(tag)
            char_offset += len(page) + 1

        return list(tags), list(url_tags), list(link_tags)


indication_tagger = IndicationTagger()
