from beanie import free_fall_migration

from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
)
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.translation_config import TranslationConfig


class Forward:
    @free_fall_migration(document_models=[])
    async def add_translation_id(self, session):
        config = await TranslationConfig.find_one(TranslationConfig.name == "Default Translation")
        if not config:
            config = TranslationConfig(name="Default Translation")
            await config.save()

        await DocDocument.get_motor_collection().update_many(
            {"translation_id": {"$exists": False}, "automated_content_extraction": True},
            {
                "$unset": {
                    "automated_content_extraction": 1,
                    "automated_content_extraction_class": 1,
                },
                "$set": {
                    "translation_id": config.id,
                },
            },
        )

        await RetrievedDocument.get_motor_collection().update_many(
            {},
            {
                "$unset": {
                    "automated_content_extraction": 1,
                    "automated_content_extraction_class": 1,
                },
            },
        )

        await ContentExtractionResult.get_motor_collection().update_many(
            {},
            {
                "$unset": {
                    "site_id": 1,
                    "retrieved_document_id": 1,
                    "scrape_task_id": 1,
                },
            },
        )
        tasks = ContentExtractionTask.get_motor_collection().find(
            {"doc_document_id": {"$exists": False}}
        )
        async for task in tasks:
            rdi = task["retrieved_document_id"]
            doc = await DocDocument.find_one(DocDocument.retrieved_document_id == rdi)
            if doc:
                await ContentExtractionTask.get_motor_collection().update_one(
                    {"_id": task["_id"]},
                    {
                        "$unset": {
                            "retrieved_document_id": True,
                            "code_column": True,
                        },
                        "$set": {
                            "doc_document_id": doc.id,
                        },
                    },
                )
            else:
                print(f"Could not find relevant DocDocument for RetrievedDocument {rdi}!")


class Backward:
    async def remove_translation_id(self, session):
        raise Exception("No Backwards Migration Set")
