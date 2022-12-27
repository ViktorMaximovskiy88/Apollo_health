import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[DocDocument, SearchCodeSet, Site])
    async def searchable_docs(self, session):
        codes: set[str] = set()
        async for code_set in SearchCodeSet.find():
            codes = codes.union(code_set.codes)

        codes = list(codes)

        searchable_sites: list[Site] = await Site.find(
            {"scrape_method_configuration.searchable": True}
        ).to_list()
        site_ids = [site.id for site in searchable_sites]

        result = await DocDocument.get_motor_collection().update_many(
            {"locations.site_id": {"$in": site_ids}, "name": {"$in": codes}},
            {"$set": {"document_type": "Medical Coverage List"}},
        )

        logging.info(
            f"DocDocument -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )

        result = await RetrievedDocument.get_motor_collection().update_many(
            {"locations.site_id": {"$in": site_ids}, "name": {"$in": codes}},
            {"$set": {"document_type": "Medical Coverage List"}},
        )
        logging.info(
            f"RetrievedDocument -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


# honestly, this is useful for testing but little else
class Backward:
    ...
