import logging
from datetime import datetime, timezone

import backend.common.models.tasks as tasks
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.models.site import Site
from backend.common.storage.client import TextStorageClient
from backend.common.tasks.task_processor import TaskProcessor
from backend.scrapeworker.doc_type_classifier import guess_doc_type


class DocTypeTaskProcessor(TaskProcessor):

    dependencies: list[str] = [
        "text_client",
    ]

    def __init__(
        self,
        logger=logging,
        text_client: TextStorageClient = TextStorageClient(),
    ) -> None:
        self.logger = logger
        self.text_client = text_client

    async def exec(self, task: tasks.DocTypeTask):
        stage_versions = await PipelineRegistry.fetch()
        doc = await DocDocument.get(task.doc_doc_id)

        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        if doc.classification_status == ApprovalStatus.APPROVED or doc.has_user_edit(
            "document_type"
        ):
            self.logger.info(f"{doc.id} classification_status={doc.classification_status} skipping")
            return

        # TODO location vs locations
        location = doc.locations[0]
        s3_key = doc.s3_text_key()
        raw_text = self.text_client.read_utf8_object(s3_key)

        site: Site = await Site.get(location.site_id)
        scrape_method_configuration = site.scrape_method_configuration if site else None

        document_type, confidence, doc_vectors, doc_type_match = guess_doc_type(
            raw_text, location.link_text, location.url, doc.name, scrape_method_configuration
        )

        current_stage = PipelineStage(
            version=stage_versions.doc_type.version,
            version_at=datetime.now(tz=timezone.utc),
        )

        if doc.pipeline_stages:
            doc.pipeline_stages.doc_type = current_stage
        else:
            doc.pipeline_stages = DocPipelineStages(doc_type=current_stage)

        updates = {
            "document_type": document_type,
            "doc_type_confidence": confidence,
            "doc_vectors": doc_vectors,
            "doc_type_match": doc_type_match.dict() if doc_type_match else None,
            "pipeline_stages": doc.pipeline_stages.dict(),
        }

        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id}, {"$set": updates}
        )
        self.logger.info(f"{doc.id} updated with doc type document_type={document_type}")
        updates.pop("doc_vectors")

        return updates

    async def get_progress(self) -> float:
        return 0.0
