import logging

import backend.common.models.tasks as tasks
from backend.common.services.lineage.core import LineageService
from backend.common.tasks.task_processor import TaskProcessor


class LineageTaskProcessor(TaskProcessor):
    def __init__(self, logger=logging) -> None:
        self.logger = logger
        self.lineage_service = LineageService(logger=logger)

    async def exec(self, task: tasks.LineageTask) -> None:
        if task.reprocess:
            await self.lineage_service.reprocess_lineage_for_site(task.site_id)
        else:
            await self.lineage_service.process_lineage_for_site(task.site_id)

    async def get_progress(self) -> float:
        return 0.0
