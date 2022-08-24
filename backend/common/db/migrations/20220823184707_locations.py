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
            {},
            [
                {
                    "$set": {
                        "locations": [
                            {
                                "base_url": "$base_url",
                                "url": "$url",
                                "site_id": "$site_id",
                                "first_collected_date": "$first_collected_date",
                                "last_collected_date": "$last_collected_date",
                                "context_metadata": "$context_metadata",
                                "link_text": "$context_metadata.link_text",
                                "closest_heading": "$context_metadata.closest_heading",
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

        # site_id
        # base_url
        # url
        # link_text
        # first_collected_date
        # last_collected_date
        # for every doc_doc

        # move all above to location
        # unset site_id, url, base_url, link_text

        # recall that old rt_ids live on doc doc and site_scrape_tasks
        # query for all dupe checksums (20!)
        # loop through pick one as the winner.
        # merge the location of the other into the winner.
        # delete the loser doc doc (by related rt id) and the loser rt itself;
        # maybe remove the rt from whatever scrape task it was in? decrement it?

        # where else might doc docs or rt docs refs live?
        # remove all change logs related to the loser rt and doc docs

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
            {},
            [
                {
                    "$set": {
                        "locations": [
                            {
                                "base_url": "$base_url",
                                "url": "$url",
                                "site_id": "$site_id",
                                "link_text": "$context_metadata.link_text",
                                "first_collected_date": "$first_collected_date",
                                "last_collected_date": "$last_collected_date",
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
