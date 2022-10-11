import re
from dataclasses import dataclass

from backend.common.core.enums import TagUpdateStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.shared import IndicationTag, TherapyTag
from backend.common.services.diff_utilities import Dmp
from backend.common.storage.client import TextStorageClient
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, digit_rgx, label_rgxs

TagList = list[TherapyTag] | list[IndicationTag]


@dataclass
class DocumentSection:
    text_area: tuple[int, int]
    id_tags: TagList
    ref_tags: TagList

    def set_section_status(self, status: TagUpdateStatus):
        for tag in self.id_tags:
            if not tag.update_status:
                tag.update_status = status
        for tag in self.ref_tags:
            if not tag.update_status:
                tag.update_status = status

    def tags_to_list(self):
        return self.id_tags + self.ref_tags


class SectionLineage:
    def __init__(
        self,
        a_section: DocumentSection,
        b_section: DocumentSection,
    ) -> None:
        self.a_section = a_section
        self.b_section = b_section
        self.diffs: list[tuple[int, str]] = []
        self.has_change: bool = False

    def _create_diff(self, a: str, b: str) -> list[tuple[int, str]]:
        dmp = Dmp()
        words = dmp.diff_wordsToChars(a, b)
        diffs = dmp.diff_main(words[0], words[1], False)
        dmp.diff_charsToLines(diffs, words[2])
        return diffs

    def _group_by_code(self, tags: TagList):
        codes: dict[int | str, TagList] = {}
        for tag in tags:
            if tag.code in codes:
                codes[tag.code].append(tag)
            else:
                codes[tag.code] = [tag]
        return codes

    def _match_and_update_tags(
        self, code: int | str, a_refs: dict[int | str, TagList], b_refs: dict[int | str, TagList]
    ):
        a_tags = a_refs[code]
        if code in b_refs:
            b_tags = b_refs[code]
            a_tags_len = len(a_tags)
            b_tags_len = len(b_tags)
            if a_tags_len == b_tags_len:
                return
            elif a_tags_len > b_tags_len:
                for i in range(b_tags_len - 1, a_tags_len - 1):
                    a_tags[i].update_status = TagUpdateStatus.ADDED
            else:
                for i in range(a_tags_len - 1, b_tags_len - 1):
                    b_tags[i].update_status = TagUpdateStatus.REMOVED
            del b_refs[code]
        else:
            for tag in a_tags:
                tag.update_status = TagUpdateStatus.ADDED

    def compare_ref_tags(self):
        a_ref_by_code = self._group_by_code(self.a_section.ref_tags)
        b_ref_by_code = self._group_by_code(self.b_section.ref_tags)
        for code in a_ref_by_code:
            self._match_and_update_tags(code, a_ref_by_code, b_ref_by_code)
        for code in b_ref_by_code:
            b_tags = b_ref_by_code[code]
            for tag in b_tags:
                tag.update_status = TagUpdateStatus.REMOVED

    def compare_text(self, a_text: str, b_text: str):
        a_text_area: str | None = None
        b_text_area: str | None = None
        if self.a_section.text_area:
            text_area_start = self.a_section.text_area[0]
            text_area_end = self.a_section.text_area[1]
            a_text_area = a_text[text_area_start:text_area_end]
        if self.b_section.text_area:
            text_area_start = self.b_section.text_area[0]
            text_area_end = self.b_section.text_area[1]
            b_text_area = b_text[text_area_start:text_area_end]

        if a_text_area and b_text_area:
            self.diffs = self._create_diff(a_text_area, b_text_area)

    def check_change(self):
        """Check if diffs contain at least one change and set has_change"""
        DIFF_EQUAL = 0
        for diff in self.diffs:
            diff_type, _ = diff
            if diff_type != DIFF_EQUAL:
                self.has_change = True
                break


class TagCompare:
    def __init__(self) -> None:
        self.text_client = TextStorageClient()

    def _partition_tags_by_type(self, tags: TagList):
        key_tags: TagList = []
        focus_tags: TagList = []
        ref_tags: TagList = []
        for tag in tags:
            if tag.key:
                key_tags.append(tag)
            elif tag.focus:
                focus_tags.append(tag)
            else:
                ref_tags.append(tag)

        if key_tags:
            ref_tags += focus_tags
            return key_tags, ref_tags

        return focus_tags, ref_tags

    def _group_by_area(
        self,
        id_tags: TagList,
        ref_tags: TagList,
    ) -> tuple[dict[tuple[int, int], DocumentSection], TagList]:
        text_areas: dict[tuple[int, int], DocumentSection] = {}
        unmatched_ref: TagList = []
        for tag in id_tags:
            if not tag.text_area:
                continue

            if tag.text_area in text_areas:
                text_areas[tag.text_area].id_tags.append(tag)
            else:
                lineage_section = DocumentSection(tag.text_area, id_tags=[tag], ref_tags=[])
                text_areas[tag.text_area] = lineage_section

        for tag in ref_tags:
            if tag.text_area and tag.text_area in text_areas:
                text_areas[tag.text_area].ref_tags.append(tag)
            else:
                unmatched_ref.append(tag)
        return text_areas, unmatched_ref

    def _group_by_section(
        self,
        id_tags: TagList,
        ref_tags: TagList,
    ):
        text_areas, unmatched_ref = self._group_by_area(id_tags, ref_tags)
        # if we need multiple sections with identical id tags, make this a list of sections
        sections: dict[frozenset[int | str], DocumentSection] = {}
        for key in text_areas:
            id_codes = [tag.code for tag in text_areas[key].id_tags]
            id_set = frozenset(id_codes)
            sections[id_set] = text_areas[key]

        return sections, unmatched_ref

    def _collect_final_tags(self, paired: list[SectionLineage], unpaired: list[DocumentSection]):
        final_tags: TagList = []
        for section in unpaired:
            final_tags += section.tags_to_list()
        for lineage in paired:
            final_tags += lineage.a_section.tags_to_list()
        return final_tags

    def _get_doc_text(self, doc: RetrievedDocument | DocDocument):
        doc_text: str = ""
        if doc.text_checksum:
            doc_text = self.text_client.read_utf8_object(f"{doc.text_checksum}.txt")
        return doc_text

    def _mark_changed(self, section_lineages: list[SectionLineage]):
        for section_lineage in section_lineages:
            if section_lineage.has_change:
                section_lineage.a_section.set_section_status(TagUpdateStatus.CHANGED)

    def _has_remove_text(self, text: str) -> bool:
        strp_text = text.strip()
        date_parser = DateParser(date_rgxs, label_rgxs)
        dates = date_parser.get_dates(strp_text)
        match = next(dates, None)
        if not match:
            match = re.match(digit_rgx, strp_text)
        return bool(match)

    def _clean_line(self, line: str):
        cleaned_line = []
        words = re.split(r"\s", line)
        for word in words:
            cleaned_word = word
            if self._has_remove_text(word):
                cleaned_word = "".join([" " for _ in word])
            cleaned_line.append(cleaned_word)
        return " ".join(cleaned_line)

    def _remove_exclude_text(self, a_text: str, b_text: str):
        cleaned_a = map(self._clean_line, a_text.split("\n"))
        cleaned_b = map(self._clean_line, b_text.split("\n"))

        return "\n".join(cleaned_a), "\n".join(cleaned_b)

    def _remove_repeat_lines(self, a_text, b_text):
        dmp = Dmp()
        lines = dmp.diff_linesToChars(a_text, b_text)
        diffs = dmp.diff_main(lines[0], lines[1], False)
        dmp.diff_charsToLines(diffs, lines[2])
        deletes, inserts = dmp.find_repeat_lines(diffs)
        return dmp.remove_diffs(deletes, inserts, a_text, b_text)

    def _preprocess_diff(self, a_text: str, b_text: str) -> tuple[str, str]:
        cleaned_a, cleaned_b = a_text, b_text
        cleaned_a, cleaned_b = self._remove_repeat_lines(cleaned_a, cleaned_b)
        cleaned_a, cleaned_b = self._remove_exclude_text(cleaned_a, cleaned_b)
        return cleaned_a, cleaned_b

    def compare_sections(
        self,
        doc_text: str,
        prev_doc_text: str,
        section_lineage: list[SectionLineage],
    ):
        for lineage in section_lineage:
            lineage.compare_ref_tags()
            lineage.compare_text(doc_text, prev_doc_text)
            lineage.check_change()

    def match_tags(
        self,
        doc_tags: TagList,
        prev_tags: TagList,
    ):

        doc_id_tags, doc_ref_tags = self._partition_tags_by_type(doc_tags)
        prev_id_tags, prev_ref_tags = self._partition_tags_by_type(prev_tags)
        doc_sections, unmatched_ref = self._group_by_section(doc_id_tags, doc_ref_tags)
        prev_sections, _ = self._group_by_section(prev_id_tags, prev_ref_tags)

        paired_sections: list[SectionLineage] = []
        unpaired_sections: list[DocumentSection] = []
        for section_key in doc_sections:
            prev_section = prev_sections.pop(section_key, None)
            if prev_section:
                pair = SectionLineage(doc_sections[section_key], prev_section)
                paired_sections.append(pair)
            else:
                doc_sections[section_key].set_section_status(TagUpdateStatus.ADDED)
                unpaired_sections.append(doc_sections[section_key])

        for prev_section in prev_sections.values():
            prev_section.set_section_status(TagUpdateStatus.REMOVED)
            unpaired_sections.append(prev_section)
        return paired_sections, unpaired_sections, unmatched_ref

    def compare_tags(
        self, doc_tags: TagList, prev_tags: TagList, doc_text: str, prev_text: str
    ) -> TagList:
        paired, unpaired, unmatched_ref = self.match_tags(doc_tags, prev_tags)
        self.compare_sections(doc_text, prev_text, paired)
        self._mark_changed(paired)
        return self._collect_final_tags(paired, unpaired) + unmatched_ref

    def execute(
        self, doc: RetrievedDocument | DocDocument, prev_doc: RetrievedDocument | DocDocument
    ):
        doc_text = self._get_doc_text(doc)
        prev_doc_text = self._get_doc_text(prev_doc)
        clean_doc_text, clean_prev_text = self._preprocess_diff(doc_text, prev_doc_text)

        final_therapy_tags: list[TherapyTag] = self.compare_tags(
            doc.therapy_tags, prev_doc.therapy_tags, clean_doc_text, clean_prev_text
        )
        final_indication_tags: list[IndicationTag] = self.compare_tags(
            doc.indication_tags, prev_doc.indication_tags, clean_doc_text, clean_prev_text
        )

        return final_therapy_tags, final_indication_tags
