from beanie import PydanticObjectId

from backend.common.models.doc_document import DocDocument


async def update_old_prev_doc_doc(updating_doc_doc: DocDocument):
    old_prev_doc_doc_id = updating_doc_doc.previous_doc_doc_id
    if not old_prev_doc_doc_id:
        return
    old_prev_doc_doc = await DocDocument.get(old_prev_doc_doc_id)

    if updating_doc_doc.is_current_version:
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": old_prev_doc_doc_id}, {"$set": {"is_current_version": True}}
        )
        old_prev_doc_doc.is_current_version = True
        return

    await DocDocument.get_motor_collection().find_one_and_update(
        {"previous_doc_doc_id": updating_doc_doc.id},
        {"$set": {"previous_doc_doc_id": old_prev_doc_doc_id}},
    )


async def update_doc_doc_and_new_prev_doc_doc(
    updating_doc_doc: DocDocument, new_prev_doc_doc_id: PydanticObjectId
):
    new_prev_doc_doc = await DocDocument.get(new_prev_doc_doc_id)

    if new_prev_doc_doc.is_current_version:
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": new_prev_doc_doc_id}, {"$set": {"is_current_version": False}}
        )
        await DocDocument.get_motor_collection().find_one_and_update(
            {"_id": updating_doc_doc.id},
            {
                "$set": {
                    "lineage_id": new_prev_doc_doc.lineage_id,
                    "previous_doc_doc_id": new_prev_doc_doc_id,
                    "is_current_version": True,
                }
            },
        )
        return

    await DocDocument.get_motor_collection().find_one_and_update(
        {"previous_doc_doc_id": new_prev_doc_doc_id},
        {"$set": {"previous_dod_doc_id": updating_doc_doc.id}},
    )

    await DocDocument.get_motor_collection().find_one_and_update(
        {"_id": updating_doc_doc.id},
        {
            "$set": {
                "lineage_id": new_prev_doc_doc.lineage_id,
                "previous_doc_doc_id": new_prev_doc_doc_id,
            }
        },
    )
