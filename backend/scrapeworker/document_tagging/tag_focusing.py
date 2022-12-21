from bisect import bisect
from dataclasses import dataclass

from spacy.tokens.span import Span

from backend.common.core.enums import DocumentType, SectionType
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import FocusSectionConfig, Site


@dataclass
class FocusArea:
    start: int
    end: int
    section_end: int
    key_text: str | None = None

    def get_text_area(self):
        return (self.end, self.section_end)


@dataclass
class FocusState:
    focus: bool
    key: bool
    section: tuple[int, int] | None
    is_in_url: bool = False
    is_in_link_text: bool = False


class FocusChecker:
    def __init__(
        self,
        full_text: str,
        focus_configs: list[FocusSectionConfig],
        url: str,
        link_text: str | None,
        doc_type: str | None = None,
    ) -> None:
        self.full_text = full_text
        self.focus_configs = focus_configs
        self.url = url
        self.link_text = link_text
        self.all_focus = self._check_all_focus(doc_type)
        self.focus_areas: list[FocusArea] = []
        self.key_areas: list[FocusArea] = []
        self.set_section_areas()

    def _check_all_focus(self, doc_type: str | None):
        all_focus_doc_types = [
            DocumentType.Formulary,
            DocumentType.FormularyUpdate,
            DocumentType.MedicalCoverageList,
            DocumentType.RestrictionList,
            DocumentType.SpecialtyList,
            DocumentType.ExclusionList,
            DocumentType.PreventiveDrugList,
            DocumentType.FeeSchedule,
            DocumentType.PayerUnlistedPolicy,
        ]
        if doc_type in all_focus_doc_types:
            return True

    @staticmethod
    async def _location_focus_configs(
        doc: RetrievedDocument | DocDocument, tag_type: SectionType
    ) -> list[FocusSectionConfig]:
        """Get unique focus configs for all locations on this doc"""
        site_ids = [location.site_id for location in doc.locations]
        sites = await Site.find({"_id": {"$in": site_ids}}).to_list()
        configs: set[FocusSectionConfig] = set()
        for site in sites:
            filtered_configs = [
                config
                for config in site.scrape_method_configuration.focus_section_configs
                if config.doc_type == doc.document_type and tag_type in config.section_type
            ]
            configs.update(filtered_configs)

        return list(configs)

    @classmethod
    async def with_all_location_configs(
        cls,
        doc: RetrievedDocument | DocDocument,
        tag_type: SectionType,
        full_text: str,
        url: str,
        link_text: str | None,
    ) -> "FocusChecker":
        """`FocusChecker` with all location's focus configs"""
        focus_configs = await cls._location_focus_configs(doc, tag_type)
        return cls(full_text, focus_configs, url, link_text, doc.document_type)

    def set_section_end(self, focus_areas: list[FocusArea]):
        for i, area in enumerate(focus_areas):
            if i < len(focus_areas) - 1:
                area.section_end = focus_areas[i + 1].start

    def _create_section_areas(self):
        focus_areas: list[FocusArea] = []
        key_areas: list[FocusArea] = []
        doc_end = len(self.full_text)
        text_lower = self.full_text.lower()
        for config in self.focus_configs:
            is_key_area = SectionType.KEY in config.section_type
            last_match = 0
            start = 0
            start_sep_is_new_page = config.start_separator == "\f"
            while True:
                # if at start of doc and separator is new page, match start of doc
                if last_match == 0 and start_sep_is_new_page:
                    match = 0
                elif config.start_separator:
                    match = text_lower.find(config.start_separator.lower(), last_match)
                else:
                    match = 0

                if match > -1:
                    if config.start_separator:
                        start = match + len(config.start_separator)
                    end = doc_end
                    if config.end_separator:
                        end_match = text_lower.find(config.end_separator.lower(), start)
                        end = end_match if end_match > -1 else end
                    focus_area = FocusArea(
                        start=start,
                        end=end,
                        section_end=doc_end,
                    )
                    if is_key_area:
                        focus_area.key_text = self.full_text[start:end]
                        key_areas.append(focus_area)
                    else:
                        focus_areas.append(focus_area)
                    last_match = end
                    if not config.start_separator:
                        break
                else:
                    break

        return focus_areas, key_areas

    def set_section_areas(self) -> None:
        focus_areas, key_areas = self._create_section_areas()

        focus_areas.sort(key=lambda area: area.start)
        key_areas.sort(key=lambda area: area.start)
        self.set_section_end(focus_areas)
        self.set_section_end(key_areas)

        self.focus_areas = focus_areas
        self.key_areas = key_areas

    def _get_sections(self, span: Span, offset: int):
        key_area: FocusArea | None = None
        focus_area: FocusArea | None = None
        section: tuple[int, int] | None = None

        start_char = span.start_char + offset
        if not self.key_areas and not self.focus_areas:
            # if sectionless document, every tag is own section
            end_char = span.end_char + offset
            section = start_char, end_char
            return key_area, focus_area, section
        key_index = bisect(self.key_areas, start_char, key=lambda area: area.start)
        focus_index = bisect(self.focus_areas, start_char, key=lambda area: area.start)
        if key_index > 0:
            key_area = self.key_areas[key_index - 1]
        if focus_index > 0:
            focus_area = self.focus_areas[focus_index - 1]

        if self.key_areas:
            if key_area:
                section = key_area.get_text_area()
        elif focus_area:
            section = focus_area.get_text_area()

        return key_area, focus_area, section

    def check_focus(self, span: Span, offset: int) -> FocusState:
        """Check span tag for focus state.
        If tag is in key area, it is a key tag."""
        key_area, focus_area, section = self._get_sections(span, offset)
        end_char = span.end_char + offset
        text = span.text.lower()
        focus_state = FocusState(focus=False, key=False, section=section)

        if key_area and end_char < key_area.end:
            focus_state.focus = True
            focus_state.key = True
        elif focus_area and end_char < focus_area.end:
            focus_state.focus = True
        elif self.all_focus:
            focus_state.focus = True

        if self.link_text and text in self.link_text.lower():
            focus_state.is_in_link_text = True
            focus_state.focus = True

        if text in self.url.lower():
            focus_state.is_in_url = True
            focus_state.focus = True

        return focus_state
