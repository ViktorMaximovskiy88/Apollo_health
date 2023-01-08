import logging

from beanie import free_fall_migration
from pymongo import UpdateOne

from backend.common.models.change_log import ChangeLog
from backend.common.models.doc_document import DocDocument


class Forward:
    @free_fall_migration(document_models=[ChangeLog, DocDocument])
    async def update_siblings_text(self, session):

        query = {"locations.siblings_text": ""}
        docs = await DocDocument.aggregate(
            aggregation_pipeline=[
                {"$match": {"locations.siblings_text": ""}},
                {"$unwind": "$locations"},
                {"$project": {"_id": 1, "locations.site_id": 1}},
            ],
        ).to_list()

        batch = []
        for doc in docs:
            query = {"_id": doc["_id"], "locations.site_id": doc["locations"]["site_id"]}
            update = {
                "$set": {"locations.$.siblings_text": None},
            }
            batch.append(UpdateOne(query, update))

        logging.info(f"{len(batch)} DocDocuments batched")
        if len(batch):
            result = await DocDocument.get_motor_collection().bulk_write(batch)
            logging.info(
                f"bulk_write -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
            )

        regex = {"$regex": "siblings_text", "$options": "i"}
        query = {"delta.path": regex, "action": "UPDATE"}
        docs = await ChangeLog.find(query).to_list()

        batch = []
        for doc in docs:
            update = {"$pull": {"delta": {"path": regex}}}
            batch.append(UpdateOne({"_id": doc.id}, update))

        logging.info(f"{len(batch)} ChangeLogs batched")
        if len(batch):
            result = await ChangeLog.get_motor_collection().bulk_write(batch)
            logging.info(
                f"bulk_write -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
            )


class Backward:
    ...
