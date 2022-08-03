from beanie import iterative_migration

from backend.common.models.content_extraction_task import ContentExtractionTask


class Forward:
    @iterative_migration()
    async def add_user_id_to_content_extraction_task(
        self, input_document: ContentExtractionTask, output_document: ContentExtractionTask
    ):
        if not input_document.user_id:
            output_document.user_id = None


class Backward:
    @iterative_migration()
    async def remove_user_id_from_content_extraction_task(
        self, input_document: ContentExtractionTask, output_document: ContentExtractionTask
    ):
        output_document.user_id = None
