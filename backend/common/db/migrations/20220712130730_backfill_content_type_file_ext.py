from beanie import iterative_migration
from backend.common.models.document import RetrievedDocument
from backend.scrapeworker.common.models import extension_to_mimetype_map


class Forward:
    @iterative_migration()
    async def backfill_content_type_file_ext(
        self,
        input_document: RetrievedDocument,
        output_document: RetrievedDocument,
    ):
        output_document.file_extension: str = (
            "pdf"
            if input_document.file_extension is None
            else input_document.file_extension
        )

        if not input_document.content_type:
            output_document.content_type = extension_to_mimetype_map[
                output_document.file_extension
            ]


class Backward:
    @iterative_migration()
    async def backfill_content_type_file_ext(
        self,
        input_document: RetrievedDocument,
        output_document: RetrievedDocument,
    ):
        pass
