import asyncio
import datetime
import re
from contextlib import contextmanager
from typing import Generator

import pdfplumber
from beanie.odm.operators.update.general import Inc, Set
from pdfplumber.page import Page

from backend.app.routes.document_sample_creator import DocumentSampleCreator
from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
    FormularyDatum,
)
from backend.common.models.doc_document import DocDocument
from backend.common.models.translation_config import TranslationConfig
from backend.common.storage.client import DocumentStorageClient
from backend.parseworker.rxnorm_entity_linker_model import rxnorm_linker


class TableContentExtractor:
    def __init__(self, doc: DocDocument, config: TranslationConfig) -> None:
        self.config = config
        self.doc = doc
        self.client = DocumentStorageClient()

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
        table_shape = self.config.extraction.table_shape
        explicit_columns = map(int, self.config.extraction.explicit_column_lines)
        return {
            "horizontal_strategy": table_shape,
            "vertical_strategy": table_shape,
            "explicit_vertical_lines": explicit_columns,
            "snap_tolerance": snap,
        }

    def extract_clean_tables(self, page: Page):
        tables = page.extract_tables(self.tablefinder_config())
        clean_tables: list[list[list[str]]] = []
        for table in tables:
            skip_rows = self.config.extraction.skip_rows
            if skip_rows:
                table = table[skip_rows:]

            header, table = self.extract_header(table)

            rtext = self.config.detection.required_header_text
            if rtext and not self.hmap(header, rtext) > 0:
                continue
            etext = self.config.detection.excluded_header_text
            if etext and self.hmap(header, etext) > 0:
                continue

            clean_table = []
            for row_n, line in enumerate(table):
                drop_line = False
                for col in self.config.extraction.required_columns:
                    if not line[self.hmap(header, col)]:
                        drop_line = True
                        break
                if drop_line:
                    continue

                for col in self.config.extraction.merge_on_missing_columns:
                    if not line[self.hmap(header, col)]:
                        if self.config.extraction.merge_strategy == "DOWN":
                            next_line = table[row_n + 1]
                            for i in range(len(next_line)):
                                next_line[i] = f"{next_line[i] or ''} {line[i] or ''}"
                            drop_line = True
                        elif self.config.extraction.merge_strategy == "UP":
                            prev_line = clean_table[-1]
                            for i in range(len(prev_line)):
                                prev_line[i] = f"{prev_line[i] or ''} {line[i] or ''}"
                            drop_line = True
                            break
                if drop_line:
                    continue
                clean_table.append(line)
            clean_tables.append(clean_table)
        return clean_tables

    def match_rule(self, rule, value):
        rgx = re.escape(rule.pattern).replace("\\*", "(.+)")
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
        codes = []
        t9n = FormularyDatum()
        for column_rules in self.config.translation.column_rules:
            value = str(line[self.hmap(header, column_rules.column)])
            value = re.sub(r"\s+", " ", value, re.MULTILINE).strip()
            for rule in column_rules.rules:
                if rule.field == "Tier":
                    for mapping in rule.mappings:
                        if value.strip() == mapping.pattern.strip():
                            t9n.tier = int(mapping.translation)
                            break
                    continue

                if rule.field == "Generic":
                    for (_, candidate, name, score) in rxnorm_linker.find_candidates([value], rule):
                        if candidate:
                            codes.append((score, candidate.concept_id, name))
                    continue

                matches, note = self.match_rule(rule, value)
                if not matches:
                    continue

                if rule.field == "PA":
                    t9n.pa = True
                    t9n.pan = note
                if rule.field == "QL":
                    t9n.ql = True
                    t9n.qln = note
                if rule.field == "ST":
                    t9n.st = True
                    t9n.stn = note
                if rule.field == "SP":
                    t9n.sp = True

        for (score, code, name) in codes:
            yield t9n.copy(update={"score": score, "code": code, "name": name})

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
                extract_task.update(Inc({ContentExtractionTask.extraction_count: 1})),
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

    async def run_extraction(self, extraction_task: ContentExtractionTask):
        filename = f"{self.doc.checksum}.pdf"
        with self.client.read_object_to_tempfile(filename) as file_path:
            for page in self.relevant_pages(file_path):
                await self.process_page(page, extraction_task)
