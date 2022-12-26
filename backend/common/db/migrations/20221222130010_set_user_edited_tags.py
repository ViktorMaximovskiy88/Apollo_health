import logging

from beanie import free_fall_migration
from pymongo import UpdateOne

from backend.common.models.change_log import ChangeLog
from backend.common.models.doc_document import DocDocument


async def find_changes(tag_type: str, output: dict):
    match = {
        "collection": "DocDocument",
        "delta.path": {"$regex": rf"/{tag_type}/\d/focus", "$options": "i"},
        "action": "UPDATE",
    }
    changed_docs = await ChangeLog.aggregate(
        aggregation_pipeline=[
            {"$match": match},
            {"$unwind": {"path": "$delta"}},
            {"$match": match},
            {
                "$group": {
                    "_id": "$target_id",
                    "log_ids": {"$addToSet": "$_id"},
                    "count": {"$count": {}},
                }
            },
        ]
    ).to_list()

    for change_doc in changed_docs:
        key = change_doc["_id"]
        if key not in output:
            output[key] = set()
        output[key].add(tag_type)

    return output


class Forward:
    @free_fall_migration(document_models=[ChangeLog, DocDocument])
    async def set_user_edited_fields(self, session):

        # first get code for changed tags by doc with log entries
        docs = {}
        docs = await find_changes("therapy_tags", docs)
        docs = await find_changes("indication_tags", docs)

        batch = []
        for id, fields in docs.items():
            update = {"user_edited_fields": {"$each": list(fields)}}
            batch.append(UpdateOne({"_id": id}, {"$addToSet": update}))

        result = await DocDocument.get_motor_collection().bulk_write(batch)
        logging.info(
            f"bulk_write -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    ...
