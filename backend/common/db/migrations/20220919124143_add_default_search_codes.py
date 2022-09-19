from beanie import free_fall_migration

from backend.common.core.enums import SearchableType
from backend.common.db.fixtures.search_codes import cpt_codes, j_codes
from backend.common.models.search_codes import SearchCodeSet


class Forward:
    @free_fall_migration(document_models=[SearchCodeSet])
    async def add_default_codes(self, session):
        initial_cpt_codes = SearchCodeSet(type=SearchableType.CPTCODES, codes=cpt_codes)
        initial_j_codes = SearchCodeSet(type=SearchableType.JCODES, codes=j_codes)
        await initial_cpt_codes.create()
        await initial_j_codes.create()


class Backward:
    @free_fall_migration(document_models=[SearchCodeSet])
    async def delete_default_codes(self, session):
        await SearchCodeSet.find({}).delete()
