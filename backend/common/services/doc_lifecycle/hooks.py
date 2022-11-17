from datetime import datetime, timezone

from beanie import PydanticObjectId

from backend.common.core.enums import ApprovalStatus
from backend.common.models.base_document import BaseModel
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import (
    ClassificationUpdateDocDocument,
    DocDocument,
    PartialDocDocumentUpdate,
    TranslationUpdateDocDocument,
    UpdateDocDocument,
)
from backend.common.models.payer_family import PayerFamily
from backend.common.services.doc_lifecycle.doc_lifecycle import DocLifecycleService
from backend.common.services.extraction.extraction_delta import DeltaCreator
from backend.common.services.lineage.update_prev_document import update_lineage
from backend.common.services.tag_compare import TagCompare
from backend.common.task_queues.unique_task_insert import try_queue_unique_task


class ChangeInfo(BaseModel):
    translation_change: bool = False
    lineage_change: PydanticObjectId | None = None
    old_payer_family_ids: list[PydanticObjectId] = []


async def recompare_tags(doc: DocDocument, prev_doc: DocDocument):
    ther_tags, indi_tags = await TagCompare().execute(doc, prev_doc)
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
    task = ContentExtractionTask(doc_document_id=doc.id, queued_time=datetime.now(tz=timezone.utc))
    inserted = await try_queue_unique_task(task, uniqueness_key="doc_document_id")
    print(inserted)


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


def update_increments(
    payer_family_increments: dict[PydanticObjectId, int],
    old_payer_family_id: PydanticObjectId,
    new_payer_family_id: PydanticObjectId,
):
    if old_payer_family_id == new_payer_family_id:
        return payer_family_increments

    payer_family_increments[old_payer_family_id] = (
        payer_family_increments[old_payer_family_id] - 1
        if old_payer_family_id in payer_family_increments
        else -1
    )

    payer_family_increments[new_payer_family_id] = (
        payer_family_increments[new_payer_family_id] + 1
        if new_payer_family_id in payer_family_increments
        else 1
    )

    return payer_family_increments


async def doc_document_save_hook(doc: DocDocument, change_info: ChangeInfo = ChangeInfo()):
    if change_info.translation_change and doc.translation_id:
        await enqueue_translation_task(doc)

    if change_info.lineage_change:
        if doc.previous_doc_doc_id:
            prev_doc = await DocDocument.get(doc.previous_doc_doc_id)
            if prev_doc:
                await recompare_tags(doc, prev_doc)
                await recompare_extractions(doc, prev_doc)

        next_doc = await DocDocument.find_one(DocDocument.previous_doc_doc_id == doc.id)
        if next_doc:
            await recompare_tags(next_doc, doc)
            await recompare_extractions(next_doc, doc)

        await update_lineage(
            updating_doc_doc=doc,
            old_prev_doc_doc_id=change_info.lineage_change,
            new_prev_doc_doc_id=doc.previous_doc_doc_id,
        )

    new_payer_family_ids = {location.payer_family_id for location in doc.locations}
    old_payer_family_ids = set(change_info.old_payer_family_ids)
    added = list(new_payer_family_ids - old_payer_family_ids)
    removed = list(old_payer_family_ids - new_payer_family_ids)
    await PayerFamily.find({"_id": {"$in": added}}).update_many({"$inc": {"doc_doc_count": 1}})
    await PayerFamily.find({"_id": {"$in": removed}}).update_many({"$inc": {"doc_doc_count": -1}})

    await DocLifecycleService().assess_document_status(doc)


def get_doc_change_info(updates: PartialDocDocumentUpdate, doc: DocDocument):
    change_info = ChangeInfo()
    if (
        isinstance(updates, (UpdateDocDocument, TranslationUpdateDocDocument))
        and updates.translation_id
    ):
        change_info.translation_change = updates.translation_id != doc.translation_id

    if (
        isinstance(updates, (UpdateDocDocument, ClassificationUpdateDocDocument))
        and updates.previous_doc_doc_id
        and updates.previous_doc_doc_id != doc.previous_doc_doc_id
    ):
        change_info.lineage_change = doc.previous_doc_doc_id

    if (
        isinstance(updates, (UpdateDocDocument))
        and (updates.locations or doc.locations)
        and (len(updates.locations) > 0 or len(doc.locations > 0))
    ):
        change_info.old_payer_family_ids = [location.payer_family_id for location in doc.locations]

    return change_info
