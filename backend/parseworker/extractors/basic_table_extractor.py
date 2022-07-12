from datetime import datetime
import re
from statistics import harmonic_mean
import pdfplumber
import redis
from beanie.odm.operators.update.general import Inc, Set
from backend.common.models.content_extraction_task import ContentExtractionResult, ContentExtractionTask, FormularyDatum
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.models.user import User
from backend.common.storage.client import DocumentStorageClient
from backend.parseworker.rxnorm_entity_linker_model import RxNormEntityLinkerModel
from backend.common.core.config import config
from backend.app.utils.logger import Logger

class BasicTableExtraction():
    def __init__(
        self,
        extract_task: ContentExtractionTask,
        retrieved_document: RetrievedDocument,
        site: Site,
        rxnorm_model: RxNormEntityLinkerModel,
    ) -> None:
        self.extract_task = extract_task
        self.site = site
        self.doc_client = DocumentStorageClient()
        self.retrieved_document = retrieved_document
        self.rxnorm_model = rxnorm_model
        self.logger = Logger()
        self.redis = redis.from_url(
            config["REDIS_URL"], password=config["REDIS_PASSWORD"]
        )
        self.user = None
        self.code_column = ''

    async def get_user(self):
        if not self.user:
            self.user = await User.by_email("admin@mmitnetwork.com")
        if not self.user:
            raise Exception("No user found")
        return self.user

    async def guess_code_column(self, table: list[list[str | None]]):
        if self.code_column:
            return self.code_column

        header = [str(h) for h in table[0]]
        cols = { h: [] for h in header }
        for line in table[1:]:
            for i, field in enumerate(header):
                cols[field].append(str(line[i]))
        n_rows = len(table)
        
        highest_score = 0
        best_column = ''
        for field, values in cols.items():
            n_unique = len(set(values))
            uniqueness = n_unique / n_rows
            candidates = self.rxnorm_model.find_candidates(values)
            n_can = 0
            for _,_,_,score in candidates:
                if score > 0.7:
                    n_can += 1
            matchness = n_can / n_rows
            score = harmonic_mean([uniqueness, matchness])
            if field and score > highest_score:
                highest_score = score
                best_column = field

        self.code_column = best_column
        await self.extract_task.update(
            Set({
                ContentExtractionTask.header: header,
                ContentExtractionTask.code_column: best_column,
            })
        )
        return best_column

    async def process_table(self, page, table: list[list[str | None]]):
        header = table[0]
        code_column = await self.guess_code_column(table)
        rows, codes = [], []
        for line in table[1:]:
            row = {}
            for i, field in enumerate(header):
                row[field] = line[i]
                if field == code_column:
                    codes.append(line[i])
            rows.append(row)

        code_candidates = self.rxnorm_model.find_candidates(codes)
        for row_number, ((text, candidate, name, score), row) in enumerate(zip(code_candidates, rows)):
            translation = FormularyDatum(score=score)
            if candidate and score > 0.5:
                translation.code = candidate.concept_id
                translation.name = name

            await self.extract_task.update(
                Inc({ContentExtractionTask.extraction_count: 1})
            )
            result = ContentExtractionResult(
                page=page.page_number,
                row=row_number,
                site_id=self.extract_task.site_id,
                scrape_task_id=self.extract_task.scrape_task_id,
                retrieved_document_id=self.extract_task.retrieved_document_id,
                content_extraction_task_id=self.extract_task.id,
                first_collected_date=datetime.now(),
                result=row,
                translation=translation
            )
            await result.save()

    def skip_table(self, table: list[list[str]]):
        cell = table[0][0]
        return cell == "$" or \
            cell == "Drug Tier" or \
            cell is None

    def clean_table(self, table: list[list[str | None]]):
        for row in table:
            for i, cell in enumerate(row):
                row[i] = re.sub(r"\s+", ' ', str(cell))
        return table
    
    async def process_page(self, page):
        tables = page.extract_tables()
        for table in tables:
            if self.skip_table(table):
                continue
            table = self.clean_table(table)
            await self.process_table(page, table)

    async def process_file(self, file_path: str):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                await self.process_page(page)

    async def run_extraction(self):
        filename = f"{self.retrieved_document.checksum}.pdf"
        with self.doc_client.read_object_to_tempfile(filename) as file_path:
            await self.process_file(file_path)
