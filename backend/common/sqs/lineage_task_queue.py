from backend.common.models.tasks import LineageTask
from backend.common.services.lineage.core import LineageService
from backend.common.sqs.base_task_queue import BaseTaskQueue


class LineageTaskQueue(BaseTaskQueue):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, class_id=LineageTask)
        self.lineage_service = LineageService(logger=self.logger)

    async def process_message(self, message: dict, body: dict):
        task = self.begin_process_message(body)

        try:
            if task.reprocess:
                await self.lineage_service.reprocess_lineage_for_site(task.site_id)
            else:
                await self.lineage_service.process_lineage_for_site(task.site_id)

        except Exception as ex:
            await self.handle_exception(ex, message, body)

        self.end_process_message(task)
