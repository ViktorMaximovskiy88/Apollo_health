from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def add_focus_to_therapy_tag(self, session):
        await DocDocument.get_motor_collection().update_many(
            {},
            {
                "$set": {"therapy_tags.$[].focus": False},
                "$unset": {"therapy_tags.$[].relevancy": ""},
            },
        )
        await RetrievedDocument.get_motor_collection().update_many(
            {},
            {
                "$set": {"therapy_tags.$[].focus": False},
                "$unset": {"therapy_tags.$[].relevancy": ""},
            },
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def remove_focus_to_therapy_tag(self, session):
        await DocDocument.get_motor_collection().update_many(
            {},
            {
                "$set": {"therapy_tags.$[].relevancy": 0.0},
                "$unset": {"therapy_tags.$[].focus": ""},
            },
        )
        await RetrievedDocument.get_motor_collection().update_many(
            {},
            {
                "$set": {"therapy_tags.$[].relevancy": 0.0},
                "$unset": {"therapy_tags.$[].focus": ""},
            },
        )
