import logging

from beanie import free_fall_migration

from backend.common.models.lineage import DocumentAnalysis


class Forward:
    @free_fall_migration(document_models=[DocumentAnalysis])
    async def clean_doc_analysis(self, session):
        result = await DocumentAnalysis.get_motor_collection().delete_many(
            {"doc_document_id": None}
        )

        logging.info(
            f"removing bad DocumentAnalysis records -> acknowledged={result.acknowledged} deleted_count={result.deleted_count}"  # noqa
        )


class Backward:
    ...
