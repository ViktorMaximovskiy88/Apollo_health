from backend.common.models.tasks import LineageTask
from backend.common.services.lineage.core import LineageService
from backend.common.sqs.base_task_queue import BaseTaskQueue


class LineageTaskQueue(BaseTaskQueue):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, class_id=LineageTask)
        self.lineage_service = LineageService(logger=self.logger)

    async def process_message(self, message: dict, body: dict):
        task = await self._get_task(body)
        task = await task.update_progress()

        try:
            self.logger.info(f"{self._task_class} processing started")

            if task.reprocess:
                await self.lineage_service.reprocess_lineage_for_site(task.site_id)
            else:
                await self.lineage_service.process_lineage_for_site(task.site_id)

            task = await task.update_finished()
            self.logger.info(f"{self._task_class} processing finished")

        except Exception as ex:
            self.logger.error(f"{self._task_class} error:", exc_info=True)
            await self.handle_exception(ex, message, body)
