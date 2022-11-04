from beanie import free_fall_migration

from backend.app.scripts.load_default_indications import create_indications
from backend.app.scripts.payer_backbone.load_payer_backbone import load_payer_backbone
from backend.common.db.init import init_db
from backend.common.models.indication import Indication
from backend.common.models.payer_backbone import PayerBackboneUnionDoc
from backend.common.models.payer_family import PayerFamily


class Forward:
    @free_fall_migration(document_models=[])
    async def reload_payers_and_indications(self, session):
        await init_db()
        await PayerBackboneUnionDoc.find_all().delete_many()
        await load_payer_backbone()

        await Indication.delete_all()
        await create_indications()

        docs = PayerFamily.get_motor_collection().find({"payer_ids.label": {"$exists": True}})
        async for doc in docs:
            doc["payer_ids"] = [d["value"] for d in doc["payer_ids"]]
            doc = PayerFamily.parse_obj(doc)
            await doc.save()


class Backward:
    pass
