import logging

import backend.common.models.tasks as tasks
from backend.common.core.utils import now
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.models.shared import get_tag_diff
from backend.common.storage.client import TextStorageClient
from backend.common.tasks.task_processor import TaskProcessor
from backend.scrapeworker.common.utils import normalize_string, tokenize_string
from backend.scrapeworker.document_tagging.indication_tagging import IndicationTagger
from backend.scrapeworker.document_tagging.taggers import Taggers, indication_tagger, therapy_tagger
from backend.scrapeworker.document_tagging.therapy_tagging import TherapyTagger

taggers = Taggers(indication=indication_tagger, therapy=therapy_tagger)


class TagTaskProcessor(TaskProcessor):

    dependencies: list[str] = [
        "text_client",
        "indication_tagger",
        "therapy_tagger",
    ]

    def __init__(
        self,
        indication_tagger: IndicationTagger | None = None,
        therapy_tagger: TherapyTagger | None = None,
        text_client: TextStorageClient | None = None,
        logger=logging,
    ) -> None:
        self.logger = logger
        self.text_client = text_client or TextStorageClient()
        self.indication_tagger = indication_tagger or taggers.indication
        self.therapy_tagger = therapy_tagger or taggers.therapy

    async def exec(self, task: tasks.TagTask):
        stage_versions = await PipelineRegistry.fetch()
        if not stage_versions:
            raise Exception("Pipeline Registry not found")

        doc = await DocDocument.get(task.doc_doc_id)

        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        if doc.get_stage_version("tag") == stage_versions.tag.version and not task.reprocess:
            return

        # TODO location vs locations
        location = doc.locations[0]
        s3_key = doc.s3_text_key()
        raw_text = self.text_client.read_utf8_object(s3_key)

        # TODO is there an opportunity to move this and stuff in docanalysis?
        link_text = normalize_string(location.link_text, url=False)
        url = normalize_string(location.url)
        tokens = tokenize_string(raw_text)

        doc_type = doc.document_type
        if not doc_type:
            raise Exception(f"No Document Type set for {doc.id}")

        (
            therapy_tags,
            url_therapy_tags,
            link_therapy_tags,
        ) = await self.therapy_tagger.tag_document(raw_text, doc_type, url, link_text, document=doc)
        (
            indication_tags,
            url_indication_tags,
            link_indication_tags,
        ) = await self.indication_tagger.tag_document(
            raw_text, doc_type, url, link_text, document=doc
        )

        current_stage = PipelineStage(
            version=stage_versions.tag.version,
            version_at=now(),
        )

        if doc.pipeline_stages:
            doc.pipeline_stages.tag = current_stage
        else:
            doc.pipeline_stages = DocPipelineStages(tag=current_stage)

        if not doc.has_user_edit("therapy_tags"):
            doc.therapy_tags = therapy_tags

        if not doc.has_user_edit("indication_tags"):
            doc.indication_tags = indication_tags

        new_therapy_tags, new_indication_tags = get_tag_diff(
            current_indication_tags=doc.indication_tags,
            current_therapy_tags=doc.therapy_tags,
            indication_tags=indication_tags,
            therapy_tags=therapy_tags,
        )

        doc = doc.process_tag_changes(new_therapy_tags, new_indication_tags)

        # Always apply priority updates
        priority = max(tag.priority for tag in therapy_tags) if therapy_tags else 0
        priority_codes = {tag.code: tag.priority for tag in therapy_tags if tag.priority}
        for tag in doc.therapy_tags:
            tag.priority = priority_codes.get(tag.code, 0)

        # TODO will be location and overall doc update..
        # we have location specific stuff...
        updates = {
            "therapy_tags": [t.dict() for t in doc.therapy_tags],
            "indication_tags": [i.dict() for i in doc.indication_tags],
            "locations.$.url_therapy_tags": [t.dict() for t in url_therapy_tags],
            "locations.$.link_therapy_tags": [t.dict() for t in link_therapy_tags],
            "locations.$.url_indication_tags": [i.dict() for i in url_indication_tags],
            "locations.$.link_indication_tags": [i.dict() for i in link_indication_tags],
            "token_count": len(tokens),
            "priority": priority,
            "pipeline_stages": doc.pipeline_stages.dict(),
        }

        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id, "locations.site_id": location.site_id}, {"$set": updates}
        )
        self.logger.debug(
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
