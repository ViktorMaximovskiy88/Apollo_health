import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def add_locations(self, session):

        # choosing to nuke any doc thats duped (20)
        # can recover via normal scrape
        checksums = []
        async for doc in RetrievedDocument.get_motor_collection().aggregate(
            [
                {"$group": {"_id": "$checksum", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
            ]
        ):
            checksums.append(doc["_id"])

        result = await RetrievedDocument.get_motor_collection().delete_many(
            {"checksum": {"$in": checksums}}
        )

        logging.info(
            f"removing dupe RetrievedDocument checksums -> acknowledged={result.acknowledged} deleted_count={result.deleted_count} checksums={len(checksums)}"  # noqa
        )

        result = await RetrievedDocument.get_motor_collection().update_many(
            {"locations": {"$exists": False}},
            [
                {
                    "$set": {
                        "locations": [
                            {
                                "base_url": "$base_url",
                                "url": "$url",
                                "link_text": "$context_metadata.link_text",
                                "closest_heading": "$context_metadata.closest_heading",
                                "site_id": "$site_id",
                                "context_metadata": "$context_metadata",
                                "first_collected_date": "$first_collected_date",
                                "last_collected_date": "$last_collected_date",
                                "previous_retrieved_doc_id": None,
                            }
                        ]
                    },
                },
                {
                    "$unset": [
                        "site_id",
                        "url",
                        "base_url",
                        "scrape_task_id",
                        "logical_document_id",
                        "logical_document_version",
                        "context_metadata",
                        "file_checksum_aliases",
                    ]
                },
            ],
        )

        logging.info(
            f"updating RetrievedDocument locations -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )

        checksums = []
        async for doc in DocDocument.get_motor_collection().aggregate(
            [
                {"$group": {"_id": "$checksum", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
            ]
        ):
            checksums.append(doc["_id"])

        result = await DocDocument.get_motor_collection().delete_many(
            {"checksum": {"$in": checksums}}
        )

        logging.info(
            f"removing dupe DocDocument checksums -> acknowledged={result.acknowledged} deleted_count={result.deleted_count} checksums={len(checksums)}"  # noqa
        )

        result = await DocDocument.get_motor_collection().update_many(
            {"locations": {"$exists": False}},
            [
                {
                    "$set": {
                        "locations": [
                            {
                                "base_url": "$base_url",
                                "url": "$url",
                                "link_text": "$link_text",
                                "closest_heading": None,
                                "site_id": "$site_id",
                                "first_collected_date": "$first_collected_date",
                                "last_collected_date": "$last_collected_date",
                                "previous_doc_doc_id": None,
                                "document_family_id": None,
                            }
                        ]
                    },
                },
                {"$unset": ["site_id", "url", "base_url", "link_text"]},
            ],
        )

        logging.info(
            f"updating DocDocument locations -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def add_locations(self, session):
        pass
