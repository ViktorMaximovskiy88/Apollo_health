from beanie import PydanticObjectId

from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
    DeltaStats,
)


class DeltaCreator:
    async def results_by_code(
        self, extract_id: PydanticObjectId | None
    ) -> dict[str, list[ContentExtractionResult]]:
        code_map: dict[str, list[ContentExtractionResult]] = {}
        results = ContentExtractionResult.find(
            {"content_extraction_task_id": extract_id, "remove": {"$ne": True}}
        )
        async for result in results:
            if result.translation and result.translation.code:
                code_map.setdefault(result.translation.code, [])
                code_map[result.translation.code].append(result)

        return code_map

    async def clear_delta(self, extract_id: PydanticObjectId | None):
        await ContentExtractionResult.find(
            {"content_extraction_task_id": extract_id, "remove": True}
        ).delete_many()
        await ContentExtractionResult.get_motor_collection().update_many(
            {"content_extraction_task_id": extract_id},
            {"$set": {"add": False}, "$unset": {"edit": True}},
        )

    def results_equal(self, result: ContentExtractionResult, prev_result: ContentExtractionResult):
        if not result.translation or not prev_result.translation:
            return False

        return result.translation == prev_result.translation

    def set_delta_fields(
        self,
        results_list: list[ContentExtractionResult],
        prev_results_list: list[ContentExtractionResult],
    ):
        if not prev_results_list:
            for result in results_list:
                result.add = True
            return

        unmatched = []
        for result in results_list:
            prev = next(
                (prev for prev in prev_results_list if self.results_equal(result, prev)), None
            )
            if prev:
                prev_results_list.remove(prev)
            else:
                unmatched.append(result)

        for result in unmatched:
            if prev_results_list:
                prev = prev_results_list.pop()
                result.edit = prev.id
            else:
                result.add = True

    def removed_copy(
        self, result: ContentExtractionResult, extract_id: PydanticObjectId | None
    ) -> ContentExtractionResult:
        return result.copy(
            update={
                "id": PydanticObjectId(),
                "content_extraction_task_id": extract_id,
                "add": False,
                "edit": None,
                "remove": True,
            }
        )

    async def compute_delta(
        self, extract: ContentExtractionTask, prev_extract: ContentExtractionTask
    ):
        await self.clear_delta(extract.id)
        prev_results_by_code = await self.results_by_code(prev_extract.id)
        results_by_code = await self.results_by_code(extract.id)

        stats = DeltaStats()

        for code, result_list in results_by_code.items():
            prev_results_list = prev_results_by_code.pop(code, [])
            self.set_delta_fields(result_list, prev_results_list)
            for result in result_list:
                stats.add_delta_stats(result)
                await result.save()

        for prev_result in prev_results_by_code.values():
            for prev in prev_result:
                removed_result = self.removed_copy(prev, extract.id)
                stats.add_delta_stats(removed_result)
                await removed_result.save()

        await extract.update({"$set": {"delta": stats}})
