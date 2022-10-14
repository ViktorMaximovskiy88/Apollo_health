from datetime import datetime

from pydantic import BaseModel

from backend.common.core.enums import ApprovalStatus
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import DocDocument, UpdateDocDocument
from backend.common.services.doc_lifecycle.doc_lifecycle import DocLifecycleService
from backend.common.services.extraction.extraction_delta import DeltaCreator
from backend.common.services.tag_compare import TagCompare
from backend.common.task_queues.unique_task_insert import try_queue_unique_task


class ChangeInfo(BaseModel):
    translation_change: bool = False
    lineage_change: bool = False


async def recompare_tags(doc: DocDocument, prev_doc: DocDocument):
    ther_tags, indi_tags = TagCompare().execute(doc, prev_doc)
    doc.therapy_tags = ther_tags
    doc.indication_tags = indi_tags
    await DocDocument.get_motor_collection().update_one(
        {"_id": doc.id},
        {
            "$set": {
                "therapy_tags": list(map(lambda t: t.dict(), ther_tags)),
                "indication_tags": list(map(lambda t: t.dict(), indi_tags)),
            }
        },
    )


async def enqueue_translation_task(doc: DocDocument):
    doc.content_extraction_task_id = None
    doc.content_extraction_status = ApprovalStatus.PENDING
    await DocDocument.get_motor_collection().update_one(
        {"_id": doc.id},
        {
            "$set": {
                "content_extraction_task_id": None,
                "content_extraction_status": ApprovalStatus.PENDING,
            }
        },
    )
    task = ContentExtractionTask(doc_document_id=doc.id, queued_time=datetime.now())
    await try_queue_unique_task(task, uniqueness_key="document_id")


async def recompare_extractions(doc: DocDocument, prev_doc: DocDocument):
    if not (doc.content_extraction_task_id and prev_doc.content_extraction_task_id):
        return

    doc.content_extraction_status = ApprovalStatus.PENDING
    await DocDocument.get_motor_collection().update_one(
        {"_id": doc.id}, {"$set": {"content_extraction_status": ApprovalStatus.PENDING}}
    )
    task = await ContentExtractionTask.get(doc.content_extraction_task_id)
    prev_task = await ContentExtractionTask.get(prev_doc.content_extraction_task_id)
    if task and prev_task:
        await DeltaCreator().compute_delta(task, prev_task)


async def doc_document_save_hook(doc: DocDocument, change_info: ChangeInfo = ChangeInfo()):
    if change_info.translation_change:
        await enqueue_translation_task(doc)

    if change_info.lineage_change and doc.previous_doc_doc_id:
        prev_doc = await DocDocument.get(doc.previous_doc_doc_id)
        if prev_doc:
            await recompare_tags(doc, prev_doc)
            await recompare_extractions(doc, prev_doc)

    await DocLifecycleService().assess_document_status(doc)


def get_doc_change_info(updates: UpdateDocDocument, doc: DocDocument):
    change_info = ChangeInfo()
    if updates.translation_id:
        change_info.translation_change = updates.translation_id != doc.translation_id
    if updates.previous_doc_doc_id:
        change_info.lineage_change = updates.previous_doc_doc_id != doc.previous_doc_doc_id

    return change_info
