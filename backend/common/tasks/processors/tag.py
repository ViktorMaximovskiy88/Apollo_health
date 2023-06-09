import logging
from typing import Any

import backend.common.models.tasks as tasks
from backend.common.core.utils import now
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry, PipelineStage
from backend.common.models.shared import DocDocumentLocation, get_tag_diff
from backend.common.services.doc_lifecycle.doc_lifecycle import DocLifecycleService
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

        # general doc tag, default to first
        if not task.site_id:
            task.site_id = doc.locations[0].site_id

        location: DocDocumentLocation | None = doc.get_site_location(task.site_id)

        if not location:
            raise Exception(f"doc_doc {doc.id} not found on site {task.site_id}")

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

        # doc tags
        new_therapy_tags, new_indication_tags = get_tag_diff(
            current_therapy_tags=doc.therapy_tags,
            current_indication_tags=doc.indication_tags,
            therapy_tags=therapy_tags,
            indication_tags=indication_tags,
        )

        # url tags
        new_url_therapy_tags, new_url_indication_tags = get_tag_diff(
            current_therapy_tags=location.url_therapy_tags,
            current_indication_tags=location.url_indication_tags,
            therapy_tags=url_therapy_tags,
            indication_tags=url_indication_tags,
        )

        # link tags
        new_link_therapy_tags, new_link_indication_tags = get_tag_diff(
            current_therapy_tags=location.link_therapy_tags,
            current_indication_tags=location.link_indication_tags,
            therapy_tags=link_therapy_tags,
            indication_tags=link_indication_tags,
        )

        has_therapy_tag_updates, has_indication_tag_updates = doc.process_tag_changes(
            new_therapy_tags=new_therapy_tags,
            new_indication_tags=new_indication_tags,
            pending_therapy_tags=therapy_tags,
            pending_indication_tags=indication_tags,
        )

        run_assess_document_status = False

        # Always apply priority updates
        has_tag_priority_update = False
        priority = max(tag.priority for tag in therapy_tags) if therapy_tags else 0
        priority_codes = {tag.code: tag.priority for tag in therapy_tags if tag.priority}
        for tag in doc.therapy_tags:
            new_priority = priority_codes.get(tag.code, 0)
            if tag.priority != new_priority:
                tag.priority = new_priority
                has_tag_priority_update = True

        if priority == 0 and indication_tags:
            priority = 1

        updates: dict[str, Any] = {
            "pipeline_stages": doc.pipeline_stages.dict(),
        }

        if has_therapy_tag_updates or has_tag_priority_update:
            updates["therapy_tags"] = [t.dict() for t in doc.therapy_tags]
            if has_therapy_tag_updates:
                run_assess_document_status = True

        if has_indication_tag_updates:
            updates["indication_tags"] = [t.dict() for t in doc.indication_tags]
            run_assess_document_status = True

        if priority != doc.priority:
            updates["priority"] = priority

        if len(tokens) != doc.token_count:
            updates["token_count"] = len(tokens)

        if len(new_link_therapy_tags):
            location.link_therapy_tags += new_link_therapy_tags
            updates["locations.$.link_therapy_tags"] = [t.dict() for t in link_therapy_tags]

        if len(new_url_therapy_tags):
            location.url_therapy_tags += new_url_therapy_tags
            updates["locations.$.url_therapy_tags"] = [t.dict() for t in url_therapy_tags]

        if len(new_link_indication_tags):
            location.link_indication_tags += new_link_indication_tags
            updates["locations.$.link_indication_tags"] = [t.dict() for t in link_indication_tags]

        if len(new_url_indication_tags):
            location.url_indication_tags += new_url_indication_tags
            updates["locations.$.url_indication_tags"] = [t.dict() for t in url_indication_tags]

        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id, "locations.site_id": location.site_id}, {"$set": updates}
        )

        # actual meaningful change, assess_document_status
        if run_assess_document_status:
            await DocLifecycleService().assess_document_status(doc)

        self.logger.debug(
            f"{doc.id} indication_tags={len(indication_tags)} therapy_tags={len(therapy_tags)}"
        )

        return {
            "therapy_tag_count": len(therapy_tags),
            "indication_tag_count": len(indication_tags),
            "token_count": len(tokens),
            "priority": priority,
            "pipeline_stages": doc.pipeline_stages.dict(),
            "run_assess_document_status": run_assess_document_status,
        }

    async def get_progress(self) -> float:
        return 0.0
