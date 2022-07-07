from typing import TypeVar
from backend.common.models.base_document import BaseDocument
from backend.common.core.enums import ScrapeTaskStatus

T = TypeVar("T", bound=BaseDocument)


async def try_queue_unique_task(task: T, uniqueness_key: str = "site_id") -> T | None:
    """
    Attempt to queue a task, if it is already queued, in progress, cancelling, return None
    """
    to_insert = task.dict()
    update_result = await task.get_motor_collection().update_one(
        {
            "site_id": to_insert[uniqueness_key],
            "status": {
                "$in": [
                    ScrapeTaskStatus.QUEUED,
                    ScrapeTaskStatus.IN_PROGRESS,
                    ScrapeTaskStatus.CANCELING,
                ]
            },
        },
        {"$setOnInsert": to_insert},
        upsert=True,
    )
    insert_id: PydanticObjectId | None = update_result.upserted_id  # type: ignore
    if insert_id:
        task.id = insert_id
        return task
    else:
        return None
