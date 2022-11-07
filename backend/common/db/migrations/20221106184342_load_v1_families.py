from beanie import free_fall_migration

from backend.app.scripts.payer_backbone.load_payer_backbone import load_payer_backbone
from backend.app.scripts.preload_families import create_families
from backend.common.db.init import init_db
from backend.common.models.payer_backbone import PayerBackboneUnionDoc


class Forward:
    @free_fall_migration(document_models=[])
    async def reload_payers_and_indications(self, session):
        await init_db()
        await PayerBackboneUnionDoc.find_all().delete_many()
        await load_payer_backbone()

        await create_families()


class Backward:
    ...
