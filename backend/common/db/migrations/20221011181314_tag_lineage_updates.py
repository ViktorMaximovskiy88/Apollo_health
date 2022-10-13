from beanie import free_fall_migration

from backend.common.core.enums import SectionType
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument, Site])
    async def update_tags(self, session):
        await RetrievedDocument.get_motor_collection().update_many(
            {
                "therapy_tags": {
                    "$elemMatch": {
                        "update_status": {"$exists": False},
                        "text_area": {"$exists": False},
                    }
                }
            },
            {
                "$set": {
                    "indication_tags.$[].focus": False,
                    "indication_tags.$[].key": False,
                    "indication_tags.$[].update_status": None,
                    "indication_tags.$[].text_area": None,
                    "therapy_tags.$[].key": False,
                    "therapy_tags.$[].update_status": None,
                    "therapy_tags.$[].text_area": None,
                }
            },
        )
        await DocDocument.get_motor_collection().update_many(
            {
                "therapy_tags": {
                    "$elemMatch": {
                        "update_status": {"$exists": False},
                        "text_area": {"$exists": False},
                    }
                }
            },
            {
                "$set": {
                    "indication_tags.$[].focus": False,
                    "indication_tags.$[].key": False,
                    "indication_tags.$[].update_status": None,
                    "indication_tags.$[].text_area": None,
                    "therapy_tags.$[].key": False,
                    "therapy_tags.$[].update_status": None,
                    "therapy_tags.$[].text_area": None,
                }
            },
        )
        await Site.get_motor_collection().update_many(
            {},
            {
                "$rename": {
                    "scrape_method_configuration.focus_therapy_configs": "scrape_method_configuration.focus_section_configs"  # noqa
                },
            },
        )
        await Site.get_motor_collection().update_many(
            {
                "scrape_method_configuration.focus_section_configs": {
                    "$elemMatch": {"section_type": {"$exists": False}},
                }
            },
            {
                "$set": {
                    "scrape_method_configuration.focus_section_configs.$[].section_type": [
                        SectionType.THERAPY
                    ]
                },
            },
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument, Site])
    async def remove_tag_updates(self, session):
        await RetrievedDocument.get_motor_collection().update_many(
            {},
            {
                "$unset": {
                    "indication_tags.$[].focus": "",
                    "indication_tags.$[].key": "",
                    "indication_tags.$[].update_status": "",
                    "indication_tags.$[].text_area": "",
                    "therapy_tags.$[].key": "",
                    "therapy_tags.$[].update_status": "",
                    "therapy_tags.$[].text_area": "",
                }
            },
        )
        await DocDocument.get_motor_collection().update_many(
            {},
            {
                "$unset": {
                    "indication_tags.$[].focus": "",
                    "indication_tags.$[].key": "",
                    "indication_tags.$[].update_status": "",
                    "indication_tags.$[].text_area": "",
                    "therapy_tags.$[].key": "",
                    "therapy_tags.$[].update_status": "",
                    "therapy_tags.$[].text_area": "",
                }
            },
        )
        await Site.get_motor_collection().update_many(
            {},
            {
                "$rename": {
                    "scrape_method_configuration.focus_section_configs": "scrape_method_configuration.focus_therapy_configs"  # noqa
                },
            },
        )
        await Site.get_motor_collection().update_many(
            {},
            {
                "$unset": {
                    "scrape_method_configuration.focus_therapy_configs.$[].section_type": ""
                },
            },
        )
