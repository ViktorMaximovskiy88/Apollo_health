import logging
from abc import ABC
from typing import Any

import backend.common.models.tasks as tasks


class TaskProcessor(ABC):
    @classmethod
    def get_dependencies(cls, container: dict[str, Any]):
        return {key: container[key] for key in cls.dependencies}

    def __init__(self, logger=logging) -> None:
        self.logger = logger

    async def exec(self, task_payload: tasks.GenericTaskType):
        raise NotImplementedError("exec is required")

    async def get_progress(self):
        raise NotImplementedError("get_progress is required")
