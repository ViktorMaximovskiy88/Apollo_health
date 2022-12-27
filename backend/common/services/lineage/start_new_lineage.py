from beanie import PydanticObjectId
from pymongo.results import UpdateResult

from backend.common.models.doc_document import DocDocument


async def start_lineage_not_include_later_documents(
    updating_doc_doc: DocDocument, old_prev_doc_doc_id: PydanticObjectId | None
) -> DocDocument:
    update_result = await updating_doc_doc.next_doc_document.update(
        {"$set": {"previous_doc_doc_id": old_prev_doc_doc_id}}
    )
    # if there is no next document, old previous is now current
    if isinstance(update_result, UpdateResult) and update_result.matched_count == 0:
        await DocDocument.find_one({"_id": old_prev_doc_doc_id}).update(
            {"$set": {"is_current_version": True}}
        )

    await DocDocument.find_one({"_id": updating_doc_doc.id}).update(
        {
            "$set": {
                "is_current_version": True,
                "lineage_id": PydanticObjectId(),
                "previous_doc_doc_id": None,
            }
        }
    )
    return updating_doc_doc


async def start_lineage_include_later_documents(
    updating_doc_doc: DocDocument, old_prev_doc_doc_id: PydanticObjectId | None
) -> DocDocument:
    await DocDocument.find_one({"_id": old_prev_doc_doc_id}).update(
        {"$set": {"is_current_version": True}}
    )

    new_lineage_id = PydanticObjectId()
    await updating_doc_doc.update(
        {
            "$set": {
                "lineage_id": new_lineage_id,
                "previous_doc_doc_id": None,
            }
        }
    )

    next_doc = await updating_doc_doc.next_doc_document
    while next_doc:
        await next_doc.update({"$set": {"lineage_id": new_lineage_id}})
        next_doc = await next_doc.next_doc_document

    return updating_doc_doc


async def start_new_lineage(
    updating_doc_doc: DocDocument,
    old_prev_doc_doc_id: PydanticObjectId | None,
    include_later_documents: bool = False,
):
    if include_later_documents:
        return await start_lineage_include_later_documents(updating_doc_doc, old_prev_doc_doc_id)
    else:
        return await start_lineage_not_include_later_documents(
            updating_doc_doc=updating_doc_doc,
            old_prev_doc_doc_id=old_prev_doc_doc_id,
        )
