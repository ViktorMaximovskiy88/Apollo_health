from beanie import free_fall_migration

from backend.common.core.enums import CollectionMethod
from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[Site])
    async def add_focus_configs_to_manual_sites(self, session):
        Site.get_motor_collection().update_many(
            {
                "collection_method": CollectionMethod.Manual,
                "scrape_method_configuration.focus_section_configs": {"$exists": False},
            },
            {"$set": {"scrape_method_configuration.focus_section_configs": []}},
        )


class Backward:
    ...
