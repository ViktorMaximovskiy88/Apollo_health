from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[DocDocument, SearchCodeSet, Site])
    async def searchable_docs(self):
        codes: set[str] = set()
        async for code_set in SearchCodeSet.find_all():
            codes = codes.union(code_set.codes)

        searchable_sites = await Site.get_motor_collection().find_all({"searchable": "True"})

        DocDocument.find({"name": {"$in": codes}}).update_many(
            {"$locations.site_id": {"$in": searchable_sites}},
            {"$set": {"document_type": "Medical Coverage List"}},
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument, SearchCodeSet])
    async def searchable_docs(self):
        codes: set[str] = set()
        async for code_set in SearchCodeSet.find_all():
            codes = codes.union(code_set.codes)

        searchable_sites = await Site.get_motor_collection().find_all({"searchable": "True"})

        DocDocument.find({"name": {"$in": codes}}).update_many(
            {"$locations.site_id": {"$in": searchable_sites}},
            {"$set": {"document_type": "Authorization Policy"}},
        )
