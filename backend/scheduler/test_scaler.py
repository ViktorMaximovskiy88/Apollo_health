from datetime import datetime
from random import random

import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.core.enums import TaskStatus
from backend.common.db.init import init_db
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.scheduler.main import get_surplus_worker_arns, identify_idle_workers, tasks_of_status


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


async def insert_scrape_task(extra_args: dict):
    task = SiteScrapeTask(site_id=PydanticObjectId(), queued_time=datetime.now())
    return await task.copy(update=extra_args).insert()


async def test_tasks_of_status():
    await insert_scrape_task({"status": TaskStatus.QUEUED})
    await insert_scrape_task({"status": TaskStatus.IN_PROGRESS})
    await insert_scrape_task({"status": TaskStatus.IN_PROGRESS})
    await insert_scrape_task({"status": TaskStatus.FAILED})
    await insert_scrape_task({"status": TaskStatus.FINISHED})

    assert await tasks_of_status(TaskStatus.QUEUED).count() == 1
    assert await tasks_of_status(TaskStatus.FAILED).count() == 1
    assert await tasks_of_status(TaskStatus.QUEUED, TaskStatus.IN_PROGRESS).count() == 3


async def test_identify_idle_workers():
    worker_arns = set(["arn1", "arn2", "arn3", "arn4"])
    await insert_scrape_task({"status": TaskStatus.IN_PROGRESS, "task_arn": "arn1"})
    await insert_scrape_task({"status": TaskStatus.FINISHED, "task_arn": "arn2"})
    await insert_scrape_task({"status": TaskStatus.CANCELING, "task_arn": "arn3"})
    await insert_scrape_task({"status": TaskStatus.FAILED, "task_arn": "arn5"})
    idle = await identify_idle_workers(worker_arns)
    assert sorted(idle) == ["arn2", "arn4"]


async def test_get_surplus_worker_arns():
    worker_arns = set(["arn1", "arn2", "arn3", "arn4", "arn5"])
    await insert_scrape_task({"status": TaskStatus.IN_PROGRESS, "task_arn": "arn1"})
    await insert_scrape_task({"status": TaskStatus.FINISHED, "task_arn": "arn2"})
    await insert_scrape_task({"status": TaskStatus.CANCELING, "task_arn": "arn3"})
    await insert_scrape_task({"status": TaskStatus.FAILED, "task_arn": "arn5"})
    surplus = await get_surplus_worker_arns(worker_arns, 4)
    free_workers = ["arn2", "arn4", "arn5"]
    assert len(surplus) == 1 and surplus[0] in free_workers
