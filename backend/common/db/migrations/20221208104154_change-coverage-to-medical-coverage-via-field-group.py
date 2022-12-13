from beanie import free_fall_migration

from backend.common.models.document_family import DocumentFamily


class Forward:
    @free_fall_migration(document_models=[DocumentFamily])
    async def change_coverage_to_medical_coverage_via_field_group(self, session):
        await DocumentFamily.get_motor_collection().update_many(
            {"field_groups": "COVERAGE"}, {"$set": {"field_groups.$": "MEDICAL_COVERAGE"}}
        )


class Backward:
    @free_fall_migration(document_models=[DocumentFamily])
    async def change_coverage_to_medical_coverage_via_field_group(self, session):
        await DocumentFamily.get_motor_collection().update_many(
            {"field_groups": {"$exists": True}},
            {"$set": {"field_groups.$[].MEDICAL_COVERAGE": "COVERAGE"}},
        )
