import logging
from datetime import datetime, timezone

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.storage.client import DocumentStorageClient, TextStorageClient
from backend.common.storage.hash import hash_full_text
from backend.common.tasks.task_processor import TaskProcessor
from backend.scrapeworker.file_parsers import get_parser_by_ext


class ContentTaskProcessor(TaskProcessor):

    dependencies: list[str] = [
        "doc_client",
        "text_client",
    ]

    def __init__(
        self,
        logger=logging,
        doc_client: DocumentStorageClient = DocumentStorageClient(),
        text_client: TextStorageClient = TextStorageClient(),
    ) -> None:
        self.logger = logger
        self.doc_client = doc_client
        self.text_client = text_client

    async def exec(self, task: tasks.ContentTask):
        stage_versions = await PipelineRegistry.fetch()
        doc = await DocDocument.get(task.doc_doc_id)

        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        #  TODO this is the gist of it

        if (
            doc.get_stage_version("content") == stage_versions.content.version
            and not task.reprocess
        ):
            return

        ParserClass = get_parser_by_ext(doc.file_extension)
        s3_key = doc.s3_doc_key()

        # TODO this will change when content includes images
        # right now text == text across sites whereas images can change that
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
        self.logger.debug(f"{doc.id} updated with text_checksum={text_hash}")
        return updates

    async def get_progress(self) -> float:
        return 0.0
