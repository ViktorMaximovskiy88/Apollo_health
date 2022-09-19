from datetime import datetime, timedelta, timezone
from random import random

import pytest
import pytest_asyncio
from beanie import PydanticObjectId
from pydantic import HttpUrl

from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
from backend.common.db.init import init_db
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.scheduler.main import (
    enqueue_scrape_task,
    find_sites_eligible_for_scraping,
    get_hung_tasks,
)


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


def simple_site(cron="0 * * * *", collection_hold=None):
    site = Site(
        name="Test",
        scrape_method="",
        scrape_method_configuration=ScrapeMethodConfiguration(
            document_extensions=[],
            url_keywords=[],
            proxy_exclusions=[],
            follow_links=False,
            follow_link_keywords=[],
            follow_link_url_keywords=[],
        ),
        disabled=False,
        cron=cron,
        base_urls=[
            BaseUrl(url=HttpUrl("https://www.example.com/", scheme="https"), status="ACTIVE")
        ],
        collection_hold=collection_hold,
    )
    return site


def simple_scrape(
    site: Site,
    status=TaskStatus.IN_PROGRESS,
    collection_method=CollectionMethod.Automated,
    last_active: datetime | None = datetime.now(tz=timezone.utc),
) -> SiteScrapeTask:
    return SiteScrapeTask(
        site_id=site.id,
        status=status,
        queued_time=datetime.now(tz=timezone.utc),
        collection_method=collection_method,
        last_active=last_active,
    )


@pytest.mark.asyncio
async def test_find_sites_for_scraping():
    cron = "0 * * * *"
    site = simple_site(cron)

    site.status = SiteStatus.NEW
    await site.save()

    crons = [cron]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 1

    # We included QUALITY_HOLD temporarily to keep running Sites
    # that were automatically changed to QUALITY_HOLD status.
    # When we remove QUALITY_HOLD status, this should change to 0.
    site.status = SiteStatus.QUALITY_HOLD
    await site.save()
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 1

    site.status = SiteStatus.ONLINE
    await site.save()
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 1

    found_site = sites[0]
    assert found_site.cron in crons
    assert found_site.disabled is False
    assert any(bu.status == "ACTIVE" for bu in found_site.base_urls)
    assert found_site.last_run_status not in [
        TaskStatus.QUEUED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELING,
    ]
    assert found_site.status == SiteStatus.ONLINE


@pytest.mark.asyncio
async def test_not_finding_inactive_sites():
    cron = "0 * * * *"
    crons = [cron]
    site = simple_site(cron)
    site.status = SiteStatus.INACTIVE
    await site.save()
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_sites_not_on_cron():
    site = simple_site("0 * * * *")
    site = await site.save()
    crons = ["15 * * * *"]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_queued_in_progress_sites():
    site_one = simple_site("0 * * * *")
    site_one.last_run_status = TaskStatus.QUEUED
    site_two = simple_site("0 * * * *")
    site_two.last_run_status = TaskStatus.IN_PROGRESS
    await site_one.save()
    await site_two.save()
    crons = ["0 * * * *"]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_sites_disabled():
    site = simple_site("3 * * * *")
    site.disabled = True
    site = await site.save()
    crons = ["0 * * * *"]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_sites_no_active_urls():
    site = simple_site("4 * * * *")
    site.base_urls[0].status = "INACTIVE"
    site = await site.save()
    crons = ["0 * * * *"]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_collection_hold():
    site = simple_site("0 * * * *")
    site.collection_hold = datetime.now(tz=timezone.utc) + timedelta(days=1)
    site = await site.save()

    site = simple_site("0 * * * *")
    site = await site.save()

    site = simple_site("0 * * * *")
    site = await site.save()
    crons = ["0 * * * *"]
    sites = await find_sites_eligible_for_scraping(crons).count()
    assert sites == 2


@pytest.mark.asyncio
async def test_enqueue_scrape_task_create_scrape_task_if_not_exists():
    site = simple_site("0 * * * *")
    site = await site.save()
    site_id: PydanticObjectId = site.id  # type: ignore
    site_scrape_task = await enqueue_scrape_task(site_id)
    assert site_scrape_task is not None

    second_site_scrape_task = await enqueue_scrape_task(site_id)
    assert second_site_scrape_task is None


class TestHungTaskChecker:
    @pytest.mark.asyncio
    async def test_get_hung_tasks(self):
        now = datetime.now(tz=timezone.utc)
        six_mins_ago = now - timedelta(minutes=6)
        site = await simple_site().save()
        await simple_scrape(site).save()
        scrape_two = await simple_scrape(site, last_active=six_mins_ago).save()

        count = 0
        async for task in get_hung_tasks(now):
            count += 1
            assert task.id == scrape_two.id
        assert count == 1

        scrape_two.last_active = now
        await scrape_two.save()
        scrape_three = await simple_scrape(
            site, status=TaskStatus.CANCELING, last_active=None
        ).save()

        count = 0
        async for task in get_hung_tasks(now):
            assert task.id == scrape_three.id
            count += 1

        assert count == 1

    @pytest.mark.asyncio
    async def test_get_no_hung_tasks(self):
        now = datetime.now(tz=timezone.utc)
        four_mins_ago = now - timedelta(minutes=4)
        ten_mins_ago = now - timedelta(minutes=10)
        site = await simple_site().save()
        await simple_scrape(site, status=TaskStatus.QUEUED, last_active=ten_mins_ago).save()
        await simple_scrape(site, status=TaskStatus.PENDING, last_active=ten_mins_ago).save()
        await simple_scrape(site, status=TaskStatus.FINISHED, last_active=ten_mins_ago).save()
        await simple_scrape(site, status=TaskStatus.FAILED, last_active=ten_mins_ago).save()
        await simple_scrape(
            site, collection_method=CollectionMethod.Manual, last_active=ten_mins_ago
        ).save()
        await simple_scrape(site, last_active=four_mins_ago).save()

        count = 0
        async for _ in get_hung_tasks(now):
            count += 1
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_hung_tasks_held_site(self):
        now = datetime.now(tz=timezone.utc)
        ten_mins_ago = now - timedelta(minutes=10)
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)

        site = await simple_site().save()
        await simple_scrape(site, last_active=ten_mins_ago).save()
        await simple_scrape(site, last_active=ten_mins_ago).save()
        await simple_scrape(site, last_active=ten_mins_ago).save()

        count = 0
        assert site.collection_hold is None
        async for _ in get_hung_tasks(now):
            count += 1
        assert count == 3

        site.collection_hold = future
        await site.save()
        count = 0
        async for _ in get_hung_tasks(now):
            count += 1
        assert count == 0

        site.collection_hold = past
        await site.save()
        count = 0
        async for _ in get_hung_tasks(now):
            count += 1
        assert count == 3
