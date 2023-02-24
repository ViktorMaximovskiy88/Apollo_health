from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.payer_family import PayerFamily


class Forward:
    @free_fall_migration(document_models=[PayerFamily, DocDocument])
    async def change_site_id_to_site_ids(self, session):
        pfs = [pf async for pf in PayerFamily.get_motor_collection().find({})]
        pf_ids = [pf["_id"] for pf in pfs]
        pfs_by_id = {pf["_id"]: pf for pf in pfs}
        family_ids_by_site = DocDocument.aggregate(
            [
                {
                    "$match": {"locations.payer_family_id": {"$in": pf_ids}},
                },
                {"$unwind": "$locations"},
                {
                    "$match": {"locations.payer_family_id": {"$in": pf_ids}},
                },
                {
                    "$group": {
                        "_id": "$locations.payer_family_id",
                        "site_ids": {"$addToSet": "$locations.site_id"},
                    }
                },
            ]
        )
        async for res in family_ids_by_site:
            id = res["_id"]
            payer_family = pfs_by_id.get(id)
            if payer_family:
                del payer_family["site_id"]
                payer_family["site_ids"] = res["site_ids"]
                payer_family = PayerFamily(**payer_family)
                await payer_family.save()


class Backward:
    ...
