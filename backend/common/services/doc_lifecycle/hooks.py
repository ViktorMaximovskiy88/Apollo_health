from datetime import datetime, timezone

from beanie import PydanticObjectId

from backend.common.core.enums import ApprovalStatus
from backend.common.models.base_document import BaseModel
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import (
    ClassificationUpdateDocDocument,
    DocDocument,
    FamilyUpdateDocDocument,
    PartialDocDocumentUpdate,
    TranslationUpdateDocDocument,
    UpdateDocDocument,
)
from backend.common.models.document_family import DocumentFamily
from backend.common.services.doc_lifecycle.doc_lifecycle import DocLifecycleService
from backend.common.services.extraction.extraction_delta import DeltaCreator
from backend.common.services.lineage.update_prev_document import update_lineage
from backend.common.services.tag_compare import TagCompare
from backend.common.task_queues.unique_task_insert import try_queue_unique_task


class ChangeInfo(BaseModel):
    translation_change: bool = False
    lineage_change: PydanticObjectId | None = None
    document_family_change: PydanticObjectId | bool = False


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


async def doc_document_save_hook(doc: DocDocument, change_info: ChangeInfo = ChangeInfo()):
    if change_info.translation_change and doc.translation_id:
        await enqueue_translation_task(doc)

    if change_info.document_family_change:
        if isinstance(change_info.document_family_change, PydanticObjectId):
            await remove_site_from_old_doc_family(change_info.document_family_change, doc)
        if doc.document_family_id:
            await add_site_to_new_doc_family(doc.document_family_id, doc)

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
        isinstance(updates, (UpdateDocDocument, FamilyUpdateDocDocument))
        and updates.document_family_id
        and updates.document_family_id != doc.document_family_id
    ):
        change_info.document_family_change = doc.document_family_id or True

    return change_info


async def add_site_to_new_doc_family(doc_fam_id: PydanticObjectId, doc: DocDocument):
    await DocumentFamily.get_motor_collection().update_one(
        {"_id": doc_fam_id},
        {"$addToSet": {"site_ids": {"$each": [location.site_id for location in doc.locations]}}},
    )


async def remove_site_from_old_doc_family(previous_doc_fam: PydanticObjectId, doc: DocDocument):
    for location in doc.locations:
        used_by_other_docs = await DocDocument.find_one(
            {
                "document_family_id": previous_doc_fam,
                "_id": {"$ne": doc.id},
                "locations": {"$elemMatch": {"site_id": location.site_id}},
            }
        )
        if not used_by_other_docs:
            await DocumentFamily.get_motor_collection().update_one(
                {"_id": previous_doc_fam}, {"$pull": {"site_ids": location.site_id}}
            )
