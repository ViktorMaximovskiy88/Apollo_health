from backend.common.models.doc_document import DocDocument
from backend.common.models.payer_family import PayerFamily
from backend.common.models.shared import DocDocumentLocation


async def update_removed_payer_family(location: DocDocumentLocation):
    if location.payer_family_id:
        locations_with_pf_and_site = await DocDocument.find_many(
            {
                "locations": {
                    "$elemMatch": {
                        "payer_family_id": location.payer_family_id,
                        "site_id": location.site_id,
                    }
                }
            }
        ).count()
        if locations_with_pf_and_site == 0:
            await PayerFamily.get_motor_collection().update_one(
                {"_id": location.payer_family_id}, {"$pull": {"site_ids": location.site_id}}
            )


async def update_added_payer_family(update_location: DocDocumentLocation):
    if update_location.payer_family_id:
        await PayerFamily.get_motor_collection().update_one(
            {"_id": update_location.payer_family_id},
            {"$addToSet": {"site_ids": update_location.site_id}},
        )


async def update_payer_family_site_ids(doc: DocDocument, old_locations: list[DocDocumentLocation]):
    if len(doc.locations) != len(old_locations):
        return
    for idx, location in enumerate(doc.locations):
        old_location = old_locations[idx]
        if location.payer_family_id == old_location.payer_family_id:
            continue

        await update_removed_payer_family(old_location)
        await update_added_payer_family(location)
