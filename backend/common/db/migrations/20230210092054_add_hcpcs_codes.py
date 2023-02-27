from beanie import free_fall_migration

from backend.common.core.enums import SearchableType
from backend.common.db.fixtures.search_codes import cpt_codes, j_codes
from backend.common.models.search_codes import SearchCodeSet


class Forward:
    @free_fall_migration(document_models=[SearchCodeSet])
    async def add_hcpcs_codes(self, session):
        await SearchCodeSet.find({"type": SearchableType.JCODES}).update(
            {"$set": {"codes": j_codes}}
        )
        await SearchCodeSet.find({"type": SearchableType.CPTCODES}).update(
            {"$set": {"codes": cpt_codes}}
        )


class Backward:
    ...
