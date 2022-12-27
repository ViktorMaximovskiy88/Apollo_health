from beanie import PydanticObjectId
from pymongo.results import UpdateResult

from backend.common.models.doc_document import DocDocument


async def get_doc_with_confidence(id: PydanticObjectId | None) -> DocDocument:
    """Convenience method for getting a DocDocument
    when you know you have a valid ObjectId but pydantic doesn't"""

    if not id:
        raise Exception("Missing 'id' Parameter")
    doc = await DocDocument.get(id)
    if not doc:
        raise Exception(f"DocDocument {id} does not exist!")

    return doc


async def insert_into_lineage_include_later_documents(
    updating_doc_doc: DocDocument,
    new_prev_doc_doc_id: PydanticObjectId | None,
    old_prev_doc_doc_id: PydanticObjectId | None,
) -> DocDocument:
    await DocDocument.find_one({"_id": old_prev_doc_doc_id}).update(
        {"$set": {"is_current_version": True}}
    )

    new_prev_doc_doc = await get_doc_with_confidence(new_prev_doc_doc_id)
    new_lineage_id = new_prev_doc_doc.lineage_id

    # Update lineage on self and all later documents
    last_document = updating_doc_doc
    while last_document:
        await last_document.update({"$set": {"lineage_id": new_lineage_id}})
        next_document = await last_document.next_doc_document
        if not next_document:
            break
        last_document = next_document

    if new_prev_doc_doc.is_current_version:
        await DocDocument.find_one({"_id": new_prev_doc_doc_id}).update(
            {"$set": {"is_current_version": False}}
        )
    else:
        await new_prev_doc_doc.next_doc_document.find_one(
            {"_id": {"$ne": updating_doc_doc.id}}
        ).update({"$set": {"previous_doc_doc_id": last_document.id}})
        last_document.is_current_version = False
        await DocDocument.find_one({"_id": last_document.id}).update(
            {"$set": {"is_current_version": False}}
        )

    await updating_doc_doc.update({"$set": {"previous_doc_doc_id": new_prev_doc_doc_id}})

    return updating_doc_doc


async def insert_into_lineage_not_include_later_documents(
    updating_doc_doc: DocDocument,
    new_prev_doc_doc_id: PydanticObjectId | None,
    old_prev_doc_doc_id: PydanticObjectId | None,
) -> DocDocument:
    update = await updating_doc_doc.next_doc_document.find_one(
        {"_id": {"$ne": updating_doc_doc.id}}
    ).update({"$set": {"previous_doc_doc_id": old_prev_doc_doc_id}})
    # if there is no next document, old previous is now current
    if isinstance(update, UpdateResult) and update.modified_count == 0:
        await DocDocument.find_one({"_id": old_prev_doc_doc_id}).update(
            {"$set": {"is_current_version": True}}
        )

    new_prev_doc_doc = await get_doc_with_confidence(new_prev_doc_doc_id)
    new_lineage = new_prev_doc_doc.lineage_id

    updating_doc_doc.lineage_id = new_lineage
    updating_doc_doc.previous_doc_doc_id = new_prev_doc_doc_id

    if new_prev_doc_doc.is_current_version:
        await new_prev_doc_doc.update({"$set": {"is_current_version": False}})
        updating_doc_doc.is_current_version = True
    else:
        await new_prev_doc_doc.next_doc_document.find_one(
            {"_id": {"$ne": updating_doc_doc.id}}
        ).update({"$set": {"previous_doc_doc_id": updating_doc_doc.id}})
        updating_doc_doc.is_current_version = False

    await DocDocument.find_one({"_id": updating_doc_doc.id}).update(
        {
            "$set": {
                "lineage_id": new_lineage,
                "previous_doc_doc_id": new_prev_doc_doc_id,
                "is_current_version": updating_doc_doc.is_current_version,
            }
        }
    )

    return updating_doc_doc
