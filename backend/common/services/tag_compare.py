import asyncio
import typing
from dataclasses import dataclass

import typer

from backend.common.core.config import env_type
from backend.common.core.enums import SectionType, TagUpdateStatus
from backend.common.core.utils import now
from backend.common.db.init import get_motor_client
from backend.common.models.doc_document import DocDocument
from backend.common.models.shared import DocumentSection, IndicationTag, TherapyTag
from backend.common.models.tag_comparison import TagComparison
from backend.common.services.text_compare.diff_utilities import Dmp
from backend.common.storage.client import TextStorageClient
from backend.scrapeworker.document_tagging.tag_focusing import FocusArea, FocusChecker

TagList = list[TherapyTag | IndicationTag]


@dataclass
class TagSection:
    text_area: tuple[int, int]
    id_tags: TagList
    ref_tags: TagList
    current_page: int | None = None
    prev_page: int | None = None
    key_text: str | None = None
    section_status: TagUpdateStatus | None = None

    def set_section_status(self, status: TagUpdateStatus):
        self.section_status = status
        if status == TagUpdateStatus.REMOVED:
            # no longer on a current page
            self.prev_page = self.current_page
            self.current_page = None
        if (
            self.section_status == TagUpdateStatus.REMOVED
            and status != TagUpdateStatus.REMOVED
            and self.current_page is None
        ):
            # reset current page if changing back from removed
            self.current_page = self.prev_page
            self.prev_page = None

        for tag in self.id_tags:
            if not tag.update_status:
                tag.update_status = status
                tag.updated_at = now()
        for tag in self.ref_tags:
            if not tag.update_status:
                tag.update_status = status
                tag.updated_at = now()

    def tags_to_list(self):
        return self.id_tags + self.ref_tags

    def to_doc_section(self) -> DocumentSection | None:
        if self.key_text is not None:
            return DocumentSection(
                key_text=self.key_text,
                section_status=self.section_status,
                current_page=self.current_page,
                prev_page=self.prev_page,
            )
        return None


class SectionLineage:
    def __init__(
        self,
        a_section: TagSection,
        b_section: TagSection,
    ) -> None:
        self.a_section = a_section
        self.b_section = b_section
        self.diffs: list[tuple[int, str]] = []
        self.has_change: bool = False
        self.dmp = Dmp()
        self.set_prev_page()

    def set_prev_page(self):
        self.a_section.prev_page = self.b_section.current_page

    def get_doc_section(self) -> DocumentSection | None:
        return self.a_section.to_doc_section()

    def _create_diff(self, a: str, b: str) -> list[tuple[int, str]]:
        words = self.dmp.diff_wordsToChars(a, b)
        diffs = self.dmp.diff_main(words[0], words[1], False)
        self.dmp.diff_charsToLines(diffs, words[2])
        return diffs

    def _concat_removed_tags(self, a_tag_list: TagList, b_tag_list: TagList):
        """Add removed tags to current document tag list"""
        removed_tags = [tag for tag in b_tag_list if tag.update_status == TagUpdateStatus.REMOVED]
        a_tag_list += removed_tags

    def _group_by_code(self, tags: TagList):
        codes: dict[int | str, TagList] = {}
        for tag in tags:
            if tag.code in codes:
                codes[tag.code].append(tag)
            else:
                codes[tag.code] = [tag]
        return codes

    def _match_and_update_tags(self, a_tags: TagList, b_tags: TagList | None):
        if b_tags is None:
            for tag in a_tags:
                tag.update_status = TagUpdateStatus.ADDED
                tag.updated_at = now()
            return

        a_tags_len = len(a_tags)
        b_tags_len = len(b_tags)
        if a_tags_len == b_tags_len:
            return
        elif a_tags_len > b_tags_len:
            for i in range(b_tags_len - 1, a_tags_len - 1):
                a_tags[i].update_status = TagUpdateStatus.ADDED
                a_tags[i].updated_at = now()
        else:
            for i in range(a_tags_len - 1, b_tags_len - 1):
                b_tags[i].update_status = TagUpdateStatus.REMOVED
                b_tags[i].updated_at = now()

    def _compare_tags(self, a_tag_list: TagList, b_tag_list: TagList):
        a_tags_by_code = self._group_by_code(a_tag_list)
        b_tags_by_code = self._group_by_code(b_tag_list)
        for code in a_tags_by_code:
            a_tags = a_tags_by_code[code]
            b_tags = b_tags_by_code.pop(code, None)
            self._match_and_update_tags(a_tags, b_tags)

        for code in b_tags_by_code:
            b_tags = b_tags_by_code[code]
            for tag in b_tags:
                tag.update_status = TagUpdateStatus.REMOVED
                tag.updated_at = now()

        self._concat_removed_tags(a_tag_list, b_tag_list)

    def compare_ref_tags(self):
        self._compare_tags(self.a_section.ref_tags, self.b_section.ref_tags)

    def compare_id_tags(self):
        if not self.a_section.key_text or not self.b_section.key_text:
            return
        self._compare_tags(self.a_section.id_tags, self.b_section.id_tags)

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


@dataclass
class TagLineage:
    therapy_tags: list[TherapyTag]
    indication_tags: list[IndicationTag]
    therapy_tag_sections: list[DocumentSection]
    indication_tag_sections: list[DocumentSection]


class TagCompare:
    THERAPY = "THERAPY"
    INDICATION = "INDICATION"

    def __init__(self) -> None:
        self.text_client = TextStorageClient()
        self.dmp = Dmp(exclude_digits=True)

    def _partition_tags_by_type(self, tags: TagList):
        focus_tags: TagList = []
        ref_tags: TagList = []
        for tag in tags:
            if tag.focus:
                focus_tags.append(tag)
            else:
                ref_tags.append(tag)

        return focus_tags, ref_tags

    def _group_by_area(
        self, id_tags: TagList, ref_tags: TagList, focus_areas: list[FocusArea]
    ) -> tuple[dict[tuple[int, int], TagSection], TagList]:
        text_areas: dict[tuple[int, int], TagSection] = {}
        for area in focus_areas:
            text_areas[area.get_text_area()] = TagSection(
                area.get_text_area(),
                current_page=area.page,
                id_tags=[],
                ref_tags=[],
                key_text=area.key_text,
            )
        unmatched_ref: TagList = []
        for tag in id_tags:
            if not tag.text_area:
                unmatched_ref.append(tag)
                continue

            if tag.text_area in text_areas:
                text_areas[tag.text_area].id_tags.append(tag)
            elif not focus_areas:
                lineage_section = TagSection(tag.text_area, id_tags=[tag], ref_tags=[])
                text_areas[tag.text_area] = lineage_section

        for tag in ref_tags:
            if tag.text_area and tag.text_area in text_areas:
                text_areas[tag.text_area].ref_tags.append(tag)
            else:
                unmatched_ref.append(tag)
        return text_areas, unmatched_ref

    def _group_by_section(self, id_tags: TagList, ref_tags: TagList, focus_areas: list[FocusArea]):
        text_areas, unmatched_ref = self._group_by_area(id_tags, ref_tags, focus_areas)
        # if document has key FocusAreas, use those to group. else use tag_codes
        sections: dict[frozenset[int | str], TagSection] = {}
        for key in text_areas:
            doc_section = text_areas[key]
            if doc_section.key_text:
                section_id = frozenset(doc_section.key_text)
            else:
                id_codes = [tag.code for tag in doc_section.id_tags]
                section_id = frozenset(id_codes)
            sections[section_id] = doc_section

        return sections, unmatched_ref

    def _collect_final_tags(self, paired: list[SectionLineage], unpaired: list[TagSection]):
        final_tags: set[IndicationTag | TherapyTag] = set()
        for section in unpaired:
            tags = section.tags_to_list()
            final_tags.update(tags)
        for lineage in paired:
            tags = lineage.a_section.tags_to_list()
            final_tags.update(tags)
        return final_tags

    def _collect_doc_sections(self, paired: list[SectionLineage], unpaired: list[TagSection]):
        def sort_tags(section: DocumentSection):
            if section.current_page is not None:
                return section.current_page
            if section.prev_page is not None:
                return section.prev_page
            return 100000

        tag_sections: list[DocumentSection] = []
        for lineage in paired:
            doc_section = lineage.get_doc_section()
            if doc_section is None:
                continue
            tag_sections.append(doc_section)
        for section in unpaired:
            doc_section = section.to_doc_section()
            if doc_section is None:
                continue
            tag_sections.append(doc_section)

        tag_sections.sort(key=sort_tags)
        return tag_sections

    def _get_doc_text(self, doc: DocDocument):
        doc_text: str = ""
        if doc.text_checksum:
            doc_text = self.text_client.read_utf8_object(f"{doc.text_checksum}.txt")
        return doc_text

    def _mark_changed(self, section_lineages: list[SectionLineage]):
        for section_lineage in section_lineages:
            if section_lineage.has_change:
                section_lineage.a_section.set_section_status(TagUpdateStatus.CHANGED)

    def compare_sections(
        self,
        doc_text: str,
        prev_doc_text: str,
        section_lineage: list[SectionLineage],
    ):
        for lineage in section_lineage:
            lineage.compare_id_tags()
            lineage.compare_ref_tags()
            lineage.compare_text(doc_text, prev_doc_text)
            lineage.check_change()

    def match_tags(
        self,
        doc_tags: TagList,
        prev_tags: TagList,
        doc_focus_areas: list[FocusArea],
        prev_focus_areas: list[FocusArea],
    ):
        doc_id_tags, doc_ref_tags = self._partition_tags_by_type(doc_tags)
        prev_id_tags, prev_ref_tags = self._partition_tags_by_type(prev_tags)
        for tag in prev_id_tags + prev_ref_tags:
            tag.update_status = None
        doc_sections, unmatched_ref = self._group_by_section(
            doc_id_tags, doc_ref_tags, doc_focus_areas
        )
        prev_sections, _ = self._group_by_section(prev_id_tags, prev_ref_tags, prev_focus_areas)

        paired_sections: list[SectionLineage] = []
        unpaired_sections: list[TagSection] = []
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

    async def _get_focus_areas(
        self, doc: DocDocument, doc_text: str, tag_type: SectionType
    ) -> list[FocusArea]:
        doc_focus_checker = await FocusChecker.with_all_location_configs(
            doc=doc, tag_type=tag_type, full_text=doc_text, url="", link_text=None
        )
        return doc_focus_checker.key_areas

    async def compare_tags(
        self,
        doc: DocDocument,
        prev_doc: DocDocument,
        doc_text: str,
        prev_text: str,
        tag_type: SectionType,
    ) -> tuple[set[IndicationTag | TherapyTag], list[DocumentSection]]:
        doc_tags = doc.therapy_tags if tag_type == SectionType.THERAPY else doc.indication_tags
        prev_tags = (
            prev_doc.therapy_tags if tag_type == SectionType.THERAPY else prev_doc.indication_tags
        )
        doc_tags = [tag for tag in doc_tags if tag.update_status != TagUpdateStatus.REMOVED]
        prev_tags = [tag for tag in prev_tags if tag.update_status != TagUpdateStatus.REMOVED]
        doc_focus_areas = await self._get_focus_areas(doc, doc_text, tag_type)
        prev_focus_areas = await self._get_focus_areas(prev_doc, prev_text, tag_type)
        paired, unpaired, unmatched_ref = self.match_tags(
            doc_tags,
            prev_tags,
            doc_focus_areas=doc_focus_areas,
            prev_focus_areas=prev_focus_areas,
        )
        self.compare_sections(doc_text, prev_text, paired)
        self._mark_changed(paired)
        final_tags = self._collect_final_tags(paired, unpaired)
        final_tags.update(unmatched_ref)
        doc_sections = self._collect_doc_sections(paired, unpaired)

        if env_type == "local":
            typer.secho(
                f"doc_focus_areas[{doc_focus_areas}], prev_focus_areas[{prev_focus_areas}], ",
                fg=typer.colors.BRIGHT_GREEN,
            )
            typer.secho(
                f"paired[{paired}], unpaired[{unpaired}], unmatched_ref[{unmatched_ref}]",
                fg=typer.colors.BRIGHT_GREEN,
            )
            typer.secho(
                f"final_tags[{final_tags}]",
                fg=typer.colors.BRIGHT_GREEN,
            )
        return final_tags, doc_sections

    async def execute(self, doc: DocDocument, prev_doc: DocDocument) -> TagLineage:
        doc_text = self._get_doc_text(doc)
        prev_doc_text = self._get_doc_text(prev_doc)
        clean_doc_text, clean_prev_text = self.dmp.preprocess_text(doc_text, prev_doc_text)

        final_therapy_tags, therapy_tag_sections = await self.compare_tags(
            doc, prev_doc, clean_doc_text, clean_prev_text, tag_type=SectionType.THERAPY
        )
        final_therapy_tags = typing.cast(set[TherapyTag], final_therapy_tags)

        final_indication_tags, indication_tag_sections = await self.compare_tags(
            doc, prev_doc, clean_doc_text, clean_prev_text, tag_type=SectionType.INDICATION
        )
        final_indication_tags = typing.cast(set[IndicationTag], final_indication_tags)

        if env_type == "local":
            typer.secho(f"clean_doc_text[{clean_doc_text}]", fg=typer.colors.BRIGHT_GREEN)
            typer.secho(f"final_therapy_tags[{final_therapy_tags}]", fg=typer.colors.BRIGHT_GREEN)
            typer.secho(
                f"final_indication_tags[{final_indication_tags}]", fg=typer.colors.BRIGHT_GREEN
            )
        return TagLineage(
            list(final_therapy_tags),
            list(final_indication_tags),
            therapy_tag_sections,
            indication_tag_sections,
        )

    async def execute_and_apply(self, doc: DocDocument, prev_doc: DocDocument) -> TagComparison:
        """
        Run tag compare and apply new tags to current DocDocument.
        Returns new TagComparison object with sections.
        Does not `save()` the documents.
        """
        tag_lineage = await self.execute(doc, prev_doc)
        doc.therapy_tags = tag_lineage.therapy_tags
        doc.indication_tags = tag_lineage.indication_tags
        return TagComparison(
            current_doc_id=doc.id,
            prev_doc_id=prev_doc.id,
            therapy_tag_sections=tag_lineage.therapy_tag_sections,
            indication_tag_sections=tag_lineage.indication_tag_sections,
        )

    async def execute_and_save(self, doc: DocDocument, prev_doc: DocDocument) -> TagLineage:
        """
        Run tag compare and apply new tags to current DocDocument.
        Upsert TagComparison object with sections.
        `.save()` the current DocDocument
        Returns the TagLineage with all data
        """
        tag_lineage = await self.execute(doc, prev_doc)
        doc.therapy_tags = tag_lineage.therapy_tags
        doc.indication_tags = tag_lineage.indication_tags
        upsert_operation = TagComparison.find_one(
            {"current_doc_id": doc.id, "prev_doc_id": prev_doc.id}
        ).upsert(
            {
                "$set": {
                    "therapy_tag_sections": tag_lineage.therapy_tag_sections,
                    "indication_tag_sections": tag_lineage.indication_tag_sections,
                }
            },
            on_insert=TagComparison(
                current_doc_id=doc.id,
                prev_doc_id=prev_doc.id,
                therapy_tag_sections=tag_lineage.therapy_tag_sections,
                indication_tag_sections=tag_lineage.indication_tag_sections,
            ),
        )
        async with await get_motor_client().start_session() as s:
            async with s.start_transaction():
                await asyncio.gather(doc.save(), upsert_operation)

        return tag_lineage
