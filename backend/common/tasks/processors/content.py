import logging
from datetime import datetime, timezone

import backend.common.models.tasks as tasks
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.storage.client import DocumentStorageClient, TextStorageClient
from backend.common.storage.hash import hash_full_text
from backend.common.tasks.task_processor import TaskProcessor
from backend.scrapeworker.file_parsers import get_parser_by_ext


class ContentTaskProcessor(TaskProcessor):
    def __init__(self, logger=logging) -> None:
        self.logger = logger
        self.doc_client = DocumentStorageClient()
        self.text_client = TextStorageClient()

    async def exec(self, task: tasks.ContentTask):
        stage_versions = await PipelineRegistry.fetch()
        # for now...
        rdoc = await RetrievedDocument.get(task.doc_doc_id)
        doc = await DocDocument.find_one(DocDocument.retrieved_document_id == rdoc.id)
        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        if doc.classification_status == ApprovalStatus.APPROVED:
            self.logger.info(f"{doc.id} classification_status={doc.classification_status} skipping")
            return

        ParserClass = get_parser_by_ext(doc.file_extension)
        s3_key = doc.s3_doc_key()
        # hate this
        location = doc.locations[0]
        with self.doc_client.read_object_to_tempfile(s3_key) as file_path:
            # TODO dont need url or link text to get text
            parser = ParserClass(file_path, location.url, location.link_text)
            doc_text = await parser.get_text()
            text_hash = hash_full_text(doc_text)

        self.text_client.write_object_mem(f"{text_hash}.txt", bytes(doc_text, "utf-8"))

        current_stage = PipelineStage(
            version=stage_versions.content.version,
            version_at=datetime.now(tz=timezone.utc),
        )

        if doc.pipeline_stages:
            doc.pipeline_stages.content = current_stage
        else:
            doc.pipeline_stages = DocPipelineStages(content=current_stage)

        updates = {
            "text_checksum": text_hash,
            "pipeline_stages": doc.pipeline_stages.dict(),
        }
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id}, {"$set": updates}
        )
        self.logger.info(f"{doc.id} updated with text_checksum={text_hash}")
        return updates

    async def get_progress(self) -> float:
        return 0.0
