import logging

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.pipeline import PipelineRegistry
from backend.common.storage.client import DocumentStorageClient, TextStorageClient
from backend.common.tasks.task_processor import TaskProcessor


class RescrapeDocProcessor(TaskProcessor):

    dependencies: list[str] = [
        "doc_client",
        "text_client",
    ]

    def __init__(
        self,
        doc_client: DocumentStorageClient | None = None,
        text_client: TextStorageClient | None = None,
        logger=logging,
    ) -> None:
        self.logger = logger
        self.doc_client = doc_client or DocumentStorageClient()
        self.text_client = text_client or TextStorageClient()

    async def exec(self, task: tasks.ContentTask):
        stage_versions = await PipelineRegistry.fetch()
        # TODO: doc_doc_id is retr_doc_id passed from pdf viewer 401 button,
        # but doc_doc_id not being set or retr_doc_id not being passed in type error.
        retr_doc = await RetrievedDocument.find_one(
            {"_id": task.doc_doc_id},
        )
        if not retr_doc:
            raise Exception(f"retr_doc {task.doc_doc_id} not found")

        doc: DocDocument | None = await DocDocument.find_one(
            {"retrieved_document_id": retr_doc.id},
        )

        if (
            doc.get_stage_version("content") == stage_versions.content.version
            and not task.reprocess
        ):
            return
