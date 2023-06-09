import logging
from datetime import datetime, timezone

import backend.common.models.tasks as tasks
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.storage.client import TextStorageClient
from backend.common.tasks.task_processor import TaskProcessor
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs


class DateTaskProcessor(TaskProcessor):

    dependencies: list[str] = [
        "text_client",
        "date_parser",
    ]

    def __init__(
        self,
        text_client: TextStorageClient | None = None,
        date_parser: DateParser | None = None,
        logger=logging,
    ) -> None:
        self.logger = logger
        self.text_client = text_client or TextStorageClient()
        self.date_parser = date_parser or DateParser(date_rgxs, label_rgxs)

    async def exec(self, task: tasks.DateTask):
        stage_versions = await PipelineRegistry.fetch()
        doc = await DocDocument.get(task.doc_doc_id)

        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        # user reviewed
        if doc.classification_status == ApprovalStatus.APPROVED or doc.has_date_user_edits():
            self.logger.info(
                f"doc_doc_id={doc.id} classification_status={doc.classification_status} skipping"
            )
            return

        # backend
        if doc.get_stage_version("date") == stage_versions.date.version and not task.reprocess:
            return

        s3_key = doc.s3_text_key()
        text = self.text_client.read_utf8_object(s3_key)
        self.date_parser.extract_dates(text)
        result = self.date_parser.as_dict()

        current_stage = PipelineStage(
            version=stage_versions.date.version,
            version_at=datetime.now(tz=timezone.utc),
        )

        if doc.pipeline_stages:
            doc.pipeline_stages.date = current_stage
        else:
            doc.pipeline_stages = DocPipelineStages(date=current_stage)

        updates = {
            **result,
            "pipeline_stages": doc.pipeline_stages.dict(),
        }
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id}, {"$set": updates}
        )
        self.logger.debug(f"{doc.id} updated with dates {result}")
        return updates

    async def get_progress(self) -> float:
        return 0.0
