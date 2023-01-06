import logging

from beanie import free_fall_migration
from pymongo import UpdateOne

from backend.common.models.change_log import ChangeLog
from backend.common.models.doc_document import DocDocument


class Forward:
    @free_fall_migration(document_models=[ChangeLog, DocDocument])
    async def set_user_edited_fields(self, session):
        user_edits_fields = [
            "/document_type",
            "/lang_code",
            "/previous_doc_doc_id",
        ]

        query = {"$match": {"delta.path": {"$in": user_edits_fields}, "action": "UPDATE"}}
        changed_docs = await ChangeLog.aggregate(
            aggregation_pipeline=[
                query,
                {"$unwind": "$delta"},
                query,
            ]
        ).to_list()

        docs = {}
        for change_doc in changed_docs:
            key = change_doc["target_id"]
            if key not in docs:
                docs[key] = set()

            field = change_doc["delta"]["path"][1:]
            docs[key].add(field)

        batch = []
        for id, fields in docs.items():
            update = {"user_edited_fields": {"$each": list(fields)}}
            batch.append(UpdateOne({"_id": id}, {"$addToSet": update}))

        if batch:
            result = await DocDocument.get_motor_collection().bulk_write(batch)
            logging.info(
                f"bulk_write -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
            )


class Backward:
    ...
