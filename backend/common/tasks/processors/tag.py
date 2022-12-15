import logging
from datetime import datetime, timezone

import backend.common.models.tasks as tasks
from backend.common.core.config import config
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.storage.client import TextStorageClient
from backend.common.tasks.task_processor import TaskProcessor
from backend.scrapeworker.common.utils import normalize_string, tokenize_string
from backend.scrapeworker.document_tagging.indication_tagging import IndicationTagger
from backend.scrapeworker.document_tagging.therapy_tagging import TherapyTagger


class TagTaskProcessor(TaskProcessor):
    def __init__(self, version: str = config["MODEL_VERSION"], logger=logging) -> None:
        self.logger = logger
        self.text_client = TextStorageClient()
        self.indication_tagger = IndicationTagger()
        self.therapy_tagger = TherapyTagger(version=version)

    async def exec(self, task: tasks.TagTask):
        stage_versions = await PipelineRegistry.fetch()
        # for now...
        rdoc = await RetrievedDocument.get(task.doc_doc_id)
        doc = await DocDocument.find_one(DocDocument.retrieved_document_id == rdoc.id)
        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        if doc.classification_status == ApprovalStatus.APPROVED:
            self.logger.info(f"{doc.id} classification_status={doc.classification_status} skipping")
            return

        # TODO location vs locations
        location = doc.locations[0]
        s3_key = doc.s3_text_key()
        raw_text = self.text_client.read_utf8_object(s3_key)

        # TODO is there an opportunity to move this and stuff in docanalysis?
        link_text = normalize_string(location.link_text, url=False)
        url = normalize_string(location.url)
        tokens = tokenize_string(raw_text)

        (
            therapy_tags,
            url_therapy_tags,
            link_therapy_tags,
        ) = await self.therapy_tagger.tag_document(
            raw_text, doc.document_type, url, link_text, document=rdoc
        )
        (
            indication_tags,
            url_indication_tags,
            link_indication_tags,
        ) = await self.indication_tagger.tag_document(
            raw_text, doc.document_type, url, link_text, document=rdoc
        )

        current_stage = PipelineStage(
            version=stage_versions.tag.version,
            version_at=datetime.now(tz=timezone.utc),
        )

        if doc.pipeline_stages:
            doc.pipeline_stages.tag = current_stage
        else:
            doc.pipeline_stages = DocPipelineStages(tag=current_stage)

        updates = {
            "therapy_tags": [t.dict() for t in therapy_tags],
            "indication_tags": [i.dict() for i in indication_tags],
            "locations.$.url_therapy_tags": [t.dict() for t in url_therapy_tags],
            "locations.$.link_therapy_tags": [t.dict() for t in link_therapy_tags],
            "locations.$.url_indication_tags": [i.dict() for i in url_indication_tags],
            "locations.$.link_indication_tags": [i.dict() for i in link_indication_tags],
            "token_count": len(tokens),
            "pipeline_stages": doc.pipeline_stages.dict(),
        }

        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id, "locations.site_id": location.site_id}, {"$set": updates}
        )
        self.logger.info(
            f"{doc.id} indication_tags={len(indication_tags)} therapy_tags={len(therapy_tags)}"
        )

        return {
            "therapy_tag_count": len(therapy_tags),
            "indication_tag_count": len(indication_tags),
            "token_count": len(tokens),
            "pipeline_stages": doc.pipeline_stages.dict(),
        }

    async def get_progress(self) -> float:
        return 0.0
