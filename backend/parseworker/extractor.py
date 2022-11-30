import asyncio
import datetime
import re
from contextlib import contextmanager
from functools import cached_property
from typing import Generator

import pdfplumber
from beanie.odm.operators.update.general import Inc, Set
from pdfplumber.page import Page

from backend.app.routes.document_sample_creator import DocumentSampleCreator
from backend.common.core.enums import TaskStatus
from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
    FormularyDatum,
)
from backend.common.models.doc_document import DocDocument
from backend.common.models.translation_config import TranslationConfig
from backend.common.services.extraction.extraction_delta import DeltaCreator
from backend.common.storage.client import DocumentStorageClient
from backend.parseworker.rxnorm_entity_linker_model import rxnorm_linker


class TableContentExtractor:
    def __init__(self, doc: DocDocument, config: TranslationConfig) -> None:
        self.config = config
        self.doc = doc

    @cached_property
    def client(self):
        return DocumentStorageClient()

    def create_doc_sample(self):
        sample_creator = DocumentSampleCreator(self.config.detection)
        sample_hash = sample_creator.sample_hash()
        sample_key = f"{self.doc.id}-sample-{sample_hash}.pdf"

        if not self.client.object_exists(sample_key):
            with self.client.read_object_to_tempfile(f"{self.doc.checksum}.pdf") as path:
                with open(path, "rb") as file:
                    sample = sample_creator.sample_file(file)
                    self.client.write_object_mem(sample_key, sample.read())

        return sample_key

    @contextmanager
    def sample_doc_page(self):
        sample_key = self.create_doc_sample()
        with self.client.read_object_to_tempfile(sample_key) as path:
            with pdfplumber.open(path) as pdf:
                yield pdf.pages[0]

    def tablefinder_config(self):
        snap = self.config.extraction.snap_tolerance
        intersect = self.config.extraction.intersection_tolerance
        table_shape = self.config.extraction.table_shape
        explicit_columns = list(map(int, self.config.extraction.explicit_column_lines))
        explicit_only = self.config.extraction.explicit_column_lines_only
        return {
            "horizontal_strategy": table_shape,
            "vertical_strategy": "explicit" if explicit_only else table_shape,
            "explicit_vertical_lines": explicit_columns,
            "snap_tolerance": snap,
            "intersection_tolerance": intersect,
        }

    def table_started(self, table_started: bool, line: list[str | None]) -> bool:
        if table_started or not self.config.extraction.start_table_text:
            return True

        for value in line:
            if value and value in self.config.extraction.start_table_text:
                return True

        return False

    def table_ended(self, line: list[str | None]) -> bool:
        end_text = self.config.extraction.end_table_text.lower()
        if not end_text:
            return False

        if end_text in "".join(map(str, line)).lower():
            return True

        return False

    def _match(self, line, header, col):
        try:
            return line[self.hmap(header, col)]
        except IndexError:
            return False

    def drop_line_if_required_or_banned(self, line, header) -> bool:
        for col in self.config.extraction.required_columns:
            if not self._match(line, header, col):
                return True
        for col in self.config.extraction.banned_columns:
            if self._match(line, header, col):
                return True
        return False

    def merge_on_missing_columns(self, line, row_n, header, table, clean_table) -> bool:
        for col in self.config.extraction.merge_on_missing_columns:
            if not self._match(line, header, col):
                if self.config.extraction.merge_strategy == "DOWN":
                    next_line = table[row_n + 1]
                    for i in range(len(next_line)):
                        next_line[i] = f"{next_line[i] or ''} {line[i] or ''}"
                    return True
                elif self.config.extraction.merge_strategy == "UP":
                    if clean_table:
                        prev_line = clean_table[-1]
                        for i in range(len(prev_line)):
                            prev_line[i] = f"{prev_line[i] or ''} {line[i] or ''}"
                    return True
        return False

    def skip_table(self, header):
        rtext = self.config.detection.required_header_text
        if rtext and not self.hmap(header, rtext) > 0:
            return True
        etext = self.config.detection.excluded_header_text
        if etext and self.hmap(header, etext) > 0:
            return True
        return False

    def extract_clean_tables(self, page: Page):
        if self.config.extraction.max_font_size:

            def filter_out_large_text(obj):
                if "size" in obj:
                    return obj["size"] < self.config.extraction.max_font_size
                return True

            page = page.filter(filter_out_large_text)

        tables = page.extract_tables(self.tablefinder_config())
        clean_tables: list[list[list[str]]] = []
        for table in tables:
            skip_rows = self.config.extraction.skip_rows
            if skip_rows:
                table = table[skip_rows:]

            header, table = self.extract_header(table)

            if self.skip_table(header):
                continue

            clean_table = []
            table_started = False
            for row_n, line in enumerate(table):
                table_started = self.table_started(table_started, line)
                if not table_started:
                    continue
                if self.table_ended(line):
                    break

                if self.drop_line_if_required_or_banned(line, header):
                    continue

                if self.merge_on_missing_columns(line, row_n, header, table, clean_table):
                    continue

                clean_table.append(line)
            clean_tables.append(clean_table)

        return clean_tables

    def match_rule(self, rule, value):
        rgx = rule.pattern.replace("(", "\\(").replace(")", "\\)").replace("*", "(.+)")
        if match := re.search(rgx, value):
            if groups := match.groups():
                return True, groups[0]
            return True, None
        return False, None

    def extract_header(self, table, drop_header=False):
        if self.config.extraction.explicit_headers:
            header = [h.lower() for h in self.config.extraction.explicit_headers]
        else:
            header = [
                re.sub(r"\s+", " ", h, re.MULTILINE).strip().lower() if h else "" for h in table[0]
            ]
            if drop_header:
                table = table[1:]
        return header, table

    def hmap(self, header, partial_header):
        lower_partial_header = partial_header.lower()
        for i, h in enumerate(header):
            if lower_partial_header in h:
                return i
        return -1

    def translate_line(self, line, header):
        brands: list[tuple[float, str, str | None, str]] = []
        generics: list[tuple[float, str, str | None, str]] = []
        t9n = FormularyDatum()
        bvg, ql_time, ql_quantity = None, None, None
        for column_rules in self.config.translation.column_rules:
            value = self._match(line, header, column_rules.column)
            if not value:
                continue
            value = re.sub(r"\s+", " ", value, re.MULTILINE).strip()
            for rule in column_rules.rules:
                if rule.field == "Tier":
                    for mapping in rule.mappings:
                        if value.strip() == mapping.pattern.strip():
                            t9n.tier = int(mapping.translation)
                            break
                    continue

                if rule.field in ["Generic", "Brand"]:
                    codes = generics if rule.field == "Generic" else brands
                    for (_, candidate, name, score) in rxnorm_linker.find_candidates([value], rule):
                        if candidate:
                            splits = candidate.concept_id.split("|")
                            drugid, rxcui = "", ""
                            if len(splits) == 1:
                                drugid = splits[0]
                            elif len(splits) == 2:
                                drugid, rxcui = splits
                            if not rxcui:
                                rxcui = None
                            codes.append((score, drugid, rxcui, name))
                    continue

                if rule.field == "BvG":
                    for mapping in rule.mappings:
                        if value.strip() == mapping.pattern:
                            bvg = mapping.translation

                if rule.field == "QLC" and value:
                    if rule.value == "time":
                        ql_time = value
                    if rule.value == "quantity":
                        ql_quantity = value
                    continue

                matches, note = self.match_rule(rule, value)
                if rule.capture_all:
                    note = value

                if not matches:
                    continue

                if rule.field == "PA":
                    t9n.pa = True
                    t9n.pan = note
                if rule.field == "PN":
                    t9n.pn = note
                if rule.field == "CPA":
                    t9n.cpa = True
                    t9n.cpan = note
                if rule.field == "QL":
                    t9n.ql = True
                    t9n.qln = note
                if rule.field == "ST":
                    t9n.st = True
                    t9n.stn = note
                if rule.field == "SP":
                    t9n.sp = True
                if rule.field == "STPA":
                    t9n.stpa = True
                if rule.field == "MB":
                    t9n.mb = True
                if rule.field == "SCO":
                    t9n.sco = True
                if rule.field == "DME":
                    t9n.dme = True

        if ql_time and ql_quantity:
            t9n.ql = True
            t9n.qln = f"{ql_quantity} / {ql_time}"

        if not bvg or bvg == "generic" or bvg == "both":
            for (score, drugid, rxcui, name) in generics:
                yield t9n.copy(
                    update={"score": score, "code": drugid, "rxcui": rxcui, "name": name}, deep=True
                )
        if not bvg or bvg == "brand" or bvg == "both":
            for (score, drugid, rxcui, name) in brands:
                yield t9n.copy(
                    update={"score": score, "code": drugid, "rxcui": rxcui, "name": name}
                )

        if not generics and not brands:
            yield t9n

    def translate_tables(
        self, tables: list[list[list[str]]]
    ) -> Generator[tuple[int, int, list[str], dict, FormularyDatum], None, None]:
        for table_number, table in enumerate(tables):
            header, table = self.extract_header(table, True)
            for row_number, line in enumerate(table):
                row = {h: line[i] for i, h in enumerate(header)}
                for translation in self.translate_line(line, header):
                    yield table_number, row_number, header, row, translation

    async def process_page(self, page: Page, extract_task: ContentExtractionTask):
        tables = self.extract_clean_tables(page)
        for table_number, row_number, header, row, t9n in self.translate_tables(tables):
            result = ContentExtractionResult(
                page=page.page_number,
                row=row_number,
                content_extraction_task_id=extract_task.id,
                first_collected_date=datetime.datetime.now(tz=datetime.timezone.utc),
                result=row,
                translation=t9n,
            )
            await asyncio.gather(
                extract_task.update(
                    Inc(
                        {
                            ContentExtractionTask.extraction_count: 1,
                            ContentExtractionTask.untranslated_count: 0 if t9n.code else 1,
                        }
                    )
                ),
                extract_task.update(Set({ContentExtractionTask.header: header})),
                result.save(),
            )

    def has_start(self, page: Page):
        start_page = self.config.detection.start_page
        if page.page_number < start_page:
            return False

        start_text = self.config.detection.start_text.lower()
        text = page.extract_text().lower()
        if start_text in text:
            return True

    def has_end(self, page: Page):
        end_page = self.config.detection.end_page
        if end_page and page.page_number > end_page:
            return False

        end_text = self.config.detection.end_text.lower()
        if not end_text:
            return False

        text = page.extract_text().lower()
        if end_text in text:
            return True

    def relevant_pages(self, file_path: str):
        found_start = False
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                if not found_start:
                    is_first_page = self.has_start(page)
                    if is_first_page:
                        found_start = True
                        yield page
                else:
                    is_last_page = self.has_end(page)
                    if is_last_page:
                        return
                    else:
                        yield page

    async def calculate_delta(self, extraction_task: ContentExtractionTask):
        await DeltaCreator().clear_delta(extraction_task.id)

        modified = []
        # Previous Doc with Extraction Exists
        prev_doc = await DocDocument.find_one({"_id": self.doc.previous_doc_doc_id})
        if prev_doc and prev_doc.content_extraction_task_id:
            prev_task = await ContentExtractionTask.get(prev_doc.content_extraction_task_id)
            if prev_task and prev_task.status == TaskStatus.FINISHED:
                await DeltaCreator().compute_delta(extraction_task, prev_task)
                modified.append(extraction_task.id)

        # Next Doc with Extraction Exists
        next_doc = await DocDocument.find_one({"previous_doc_doc_id": self.doc.id})
        if next_doc and next_doc.content_extraction_task_id:
            next_task = await ContentExtractionTask.get(next_doc.content_extraction_task_id)
            if next_task and next_task.status == TaskStatus.FINISHED:
                await DeltaCreator().compute_delta(next_task, extraction_task)
                modified.append(next_task.id)

        return modified

    async def run_extraction(self, extraction_task: ContentExtractionTask):
        filename = f"{self.doc.checksum}.pdf"
        with self.client.read_object_to_tempfile(filename) as file_path:
            for page in self.relevant_pages(file_path):
                await self.process_page(page, extraction_task)
