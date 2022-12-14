import asyncio
import tempfile

import spacy
from spacy.tokens.span import Span

from backend.common.core.config import config
from backend.common.core.enums import SectionType
from backend.common.models.doc_document import DocDocument, TherapyTag
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import FocusSectionConfig
from backend.common.storage.client import ModelStorageClient
from backend.scrapeworker.document_tagging.tag_focusing import FocusChecker

TRADEMARK_SYMBOLS = ["\u00AE", "\u2122", "\24C7"]


class TherapyTagger:
    def __init__(self, version="latest") -> None:
        self.nlp = None
        try:
            self.client = ModelStorageClient()
            self.tempdir = tempfile.TemporaryDirectory()
            dirname = self.tempdir.name
            self.client.download_directory(f"{version}/rxnorm-span", dirname)
            self.nlp = spacy.load(dirname)
            # This limit assumes the default large NER model is being used
            # We are not using this model so safe to bump limit
            # saw a value of 20074378... bumping more
            self.nlp.max_length = 300000000
        except Exception:
            print("RxNorm Span Ruler Model not found and therefore not loaded")

    def clean_page(self, page: str):
        for symbol in TRADEMARK_SYMBOLS:
            page = page.replace(symbol, " ")
        return page

    def _filter_focus_configs(self, configs: list[FocusSectionConfig], doc_type: str):
        filtered = [
            config
            for config in configs
            if config.doc_type == doc_type and (SectionType.THERAPY in config.section_type)
        ]
        return filtered

    async def tag_document(
        self,
        full_text: str,
        doc_type: str,
        url: str,
        link_text: str | None,
        focus_configs: list[FocusSectionConfig] | None = None,
        document: RetrievedDocument | DocDocument | None = None,
    ) -> tuple[list[TherapyTag], list[TherapyTag], list[TherapyTag]]:
        if not self.nlp:
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
            doc = await loop.run_in_executor(None, self.nlp, page)
            span: Span
            for span in doc.spans.get("sc", []):
                focus_state = focus_checker.check_focus(span, offset=char_offset)
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

                if focus_state.is_in_link_text or focus_state.is_in_url:
                    context_tag = TherapyTag(
                        text=text.lower(),
                        code=drugid,
                        rxcui=rxcui,
                        name=display_name,
                        page=-1,
                        focus=focus_state.focus,
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
                    text_area=focus_state.section,
                )
                tags.add(tag)
            char_offset += len(page) + 1

        return list(tags), list(url_tags), list(link_tags)


therapy_tagger = TherapyTagger(version=config["MODEL_VERSION"])
