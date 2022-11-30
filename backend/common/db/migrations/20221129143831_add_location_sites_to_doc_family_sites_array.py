from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily


class Forward:
    @free_fall_migration(document_models=[DocDocument, DocumentFamily])
    async def add_locations_to_doc_family_sites_array(self, session):

        family_ids_by_site = DocDocument.aggregate(
            [
                {
                    "$match": {
                        "$and": [
                            {"document_family_id": {"$ne": None}},
                            {"document_family_id": {"$exists": True}},
                        ]
                    }
                },
                {"$unwind": "$locations"},
                {
                    "$group": {
                        "_id": "$document_family_id",
                        "site_ids": {"$addToSet": "$locations.site_id"},
                    }
                },
            ]
        )
        async for res in family_ids_by_site:
            if not res["_id"]:
                continue
            doc_family = await DocumentFamily.get(res["_id"])
            doc_family.site_ids = res["site_ids"]
            await doc_family.save()


class Backward:
    ...
