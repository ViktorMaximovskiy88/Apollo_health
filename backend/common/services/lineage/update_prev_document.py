from typing import Any

from beanie import PydanticObjectId
from pymongo import ReturnDocument

from backend.common.models.doc_document import DocDocument


async def update_old_prev_doc_doc(old_prev_doc_doc_id: PydanticObjectId | None):
    if not old_prev_doc_doc_id:
        return
    await DocDocument.get_motor_collection().find_one_and_update(
        {"_id": old_prev_doc_doc_id}, {"$set": {"is_current_version": True}}
    )


async def get_doc_with_confidence(id: PydanticObjectId | None) -> DocDocument:
    """Convenience method for getting a DocDocument
    when you know you have a valid ObjectId but pydantic doesn't"""

    if not id:
        raise Exception("Missing 'id' Parameter")
    doc = await DocDocument.get(id)
    if not doc:
        raise Exception(f"DocDocument {id} does not exist!")

    return doc


async def update_ancestors_lineage(
    updated_doc_doc: dict[str, Any],  # dict of DocDocument
) -> DocDocument:  # earliest ancestor
    updated_ancestor = await DocDocument.get_motor_collection().find_one_and_update(
        {"previous_doc_doc_id": updated_doc_doc["_id"]},
        {"$set": {"lineage_id": updated_doc_doc["lineage_id"]}},
        projection={"_id": 1, "lineage_id": 1, "previous_doc_doc_id": 1},
        return_document=ReturnDocument.AFTER,
    )
    if not updated_ancestor:
        return await get_doc_with_confidence(updated_doc_doc["_id"])
    return await update_ancestors_lineage(updated_ancestor)


async def update_doc_doc_and_new_prev_doc_doc(
    updating_doc_doc: DocDocument, new_prev_doc_doc_id: PydanticObjectId
) -> DocDocument:
    new_prev_doc_doc = await get_doc_with_confidence(new_prev_doc_doc_id)

    if new_prev_doc_doc.is_current_version:
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": new_prev_doc_doc_id}, {"$set": {"is_current_version": False}}
        )
        updated_doc_doc = await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": updating_doc_doc.id},
            {
                "$set": {
                    "lineage_id": new_prev_doc_doc.lineage_id,
                    "previous_doc_doc_id": new_prev_doc_doc_id,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return await update_ancestors_lineage(updated_doc_doc)

    if not new_prev_doc_doc.is_current_version and updating_doc_doc.is_current_version:
        await DocDocument.get_motor_collection().find_one_and_update(
            {"previous_doc_doc_id": new_prev_doc_doc_id},
            {"$set": {"previous_doc_doc_id": updating_doc_doc.id}},
        )
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": updating_doc_doc.id},
            {
                "$set": {
                    "lineage_id": new_prev_doc_doc.lineage_id,
                    "previous_doc_doc_id": new_prev_doc_doc_id,
                    "is_current_version": False,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return await get_doc_with_confidence(updating_doc_doc.id)

    # neither is_current_version
    new_parent_of_inserted_documents = await DocDocument.find_one(
        {"previous_doc_doc_id": new_prev_doc_doc_id}
    )
    updated_doc_doc = await DocDocument.get_motor_collection().find_one_and_update(
        {"_id": updating_doc_doc.id},
        {
            "$set": {
                "lineage_id": new_prev_doc_doc.lineage_id,
                "previous_doc_doc_id": new_prev_doc_doc_id,
            }
        },
        projection={"_id": 1, "lineage_id": 1, "previous_doc_doc_id": 1},
        return_document=ReturnDocument.AFTER,
    )
    updated_earliest_ancestor = await update_ancestors_lineage(updated_doc_doc)
    await DocDocument.get_motor_collection().find_one_and_update(
        {"_id": updated_earliest_ancestor.id}, {"$set": {"is_current_version": False}}
    )
    await DocDocument.get_motor_collection().find_one_and_update(
        {"_id": new_parent_of_inserted_documents.id},  # type: ignore
        {"$set": {"previous_doc_doc_id": updated_earliest_ancestor.id}},
    )
    return await get_doc_with_confidence(updating_doc_doc.id)


async def update_lineage(
    updating_doc_doc: DocDocument,
    old_prev_doc_doc_id: PydanticObjectId | None,
    new_prev_doc_doc_id: PydanticObjectId | None,
):
    if not new_prev_doc_doc_id:
        return updating_doc_doc
    if old_prev_doc_doc_id == new_prev_doc_doc_id:
        return updating_doc_doc
    await update_old_prev_doc_doc(old_prev_doc_doc_id)
    updated_doc_doc = await update_doc_doc_and_new_prev_doc_doc(
        updating_doc_doc=updating_doc_doc, new_prev_doc_doc_id=new_prev_doc_doc_id
    )
    return updated_doc_doc
