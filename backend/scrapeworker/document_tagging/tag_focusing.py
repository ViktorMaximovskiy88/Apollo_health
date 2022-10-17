from bisect import bisect
from dataclasses import dataclass

from spacy.tokens.span import Span

from backend.common.core.enums import SectionType
from backend.common.models.site import FocusSectionConfig


@dataclass
class FocusArea:
    start: int
    end: int
    section_end: int


@dataclass
class FocusState:
    focus: bool
    key: bool
    section: tuple[int, int] | None


class FocusChecker:
    def __init__(
        self,
        full_text: str,
        focus_configs: list[FocusSectionConfig],
        url: str,
        link_text: str | None,
    ) -> None:
        self.full_text = full_text
        self.focus_configs = focus_configs
        self.url = url
        self.link_text = link_text
        self.all_focus = self._check_all_focus()
        self.focus_areas: list[FocusArea] = []
        self.key_areas: list[FocusArea] = []
        self.set_section_areas()

    def _check_all_focus(self):
        for config in self.focus_configs:
            if config.all_focus is True:
                return True

        return False

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
        key_index = bisect(self.key_areas, start_char, key=lambda area: area.start)
        focus_index = bisect(self.focus_areas, start_char, key=lambda area: area.start)
        if key_index > 0:
            key_area = self.key_areas[key_index - 1]
        if focus_index > 0:
            focus_area = self.focus_areas[focus_index - 1]

        if self.key_areas:
            if key_area:
                section = key_area.end, key_area.section_end
        elif focus_area:
            section = focus_area.end, focus_area.section_end

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
        elif self.link_text and text in self.link_text.lower():
            focus_state.focus = True
        elif text in self.url.lower():
            focus_state.focus = True

        return focus_state
