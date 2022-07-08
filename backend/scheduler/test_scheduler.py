from beanie import PydanticObjectId
from pydantic import HttpUrl
import pytest
import pytest_asyncio

from backend.common.db.init import init_db, get_motor_db, get_motor_client
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.scheduler.main import enqueue_scrape_task, find_sites_eligible_for_scraping
from backend.common.core.enums import SiteStatus
from backend.common.core.enums import TaskStatus
from random import random


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


def simple_site(cron):
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
            BaseUrl(
                url=HttpUrl("https://www.example.com/", scheme="https"), status="ACTIVE"
            )
        ],
    )
    return site


@pytest.mark.asyncio
async def test_find_sites_for_scraping():
    cron = "0 * * * *"
    site = simple_site(cron)
    site.status = SiteStatus.ONLINE
    await site.save()
    crons = [cron]
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
async def test_not_finding_sites_not_on_cron():
    site = simple_site("0 * * * *")
    site = await site.save()
    crons = ["15 * * * *"]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_queued_sites():
    cron = "0 * * * *"
    site = simple_site(cron)
    site.last_run_status = TaskStatus.QUEUED
    site = await site.save()
    crons = [cron]
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_sites_not_online():
    cron = "0 * * * *"
    crons = [cron]

    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0

    site = simple_site(cron)  # default SiteStatus is SiteStatus.NEW
    await site.save()
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0

    site = simple_site(cron)
    site.status = SiteStatus.QUALITY_HOLD
    await site.save()
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0

    site = simple_site(cron)
    site.status = SiteStatus.INACTIVE
    await site.save()
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_not_finding_sites_already_queued():
    site = simple_site("0 * * * *")
    site.last_run_status = TaskStatus.QUEUED
    site = await site.save()
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
async def test_enqueue_scrape_task_create_scrape_task_if_not_exists():
    site = simple_site("0 * * * *")
    site = await site.save()
    site_id: PydanticObjectId = site.id  # type: ignore
    site_scrape_task = await enqueue_scrape_task(site_id)
    assert site_scrape_task is not None

    second_site_scrape_task = await enqueue_scrape_task(site_id)
    assert second_site_scrape_task is None
