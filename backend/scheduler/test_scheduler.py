from tkinter import simpledialog
from beanie import PydanticObjectId
from pydantic import HttpUrl
import pytest

from backend.common.db.init import init_db
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.scheduler.main import enqueue_scrape_task, find_sites_eligible_for_scraping


def simple_site(cron):
    site = Site(
        name="Test",
        scrape_method='',
        scrape_method_configuration=ScrapeMethodConfiguration(
          document_extensions=[],
          url_keywords=[]  
        ),
        disabled=False,
        cron=cron,
        base_urls=[
            BaseUrl(
                url=HttpUrl("https://www.example.com/", scheme='https'),
                status='ACTIVE'
            )
        ],
    )
    return site

@pytest.mark.asyncio
async def test_find_sites_for_scraping():
    await init_db(mock=True)
    site = simple_site(cron='0 * * * *')
    await site.save()
    crons = ['0 * * * *']
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 1
    found_site = sites[0]
    assert found_site.cron in crons
    assert found_site.disabled is False
    assert any(bu.status == 'ACTIVE' for bu in found_site.base_urls)
    assert found_site.last_status not in ['QUEUED', 'IN_PROGRESS', 'CANCELLING']

@pytest.mark.asyncio
async def test_not_finding_sites_not_on_cron():
    await init_db(mock=True)
    site = simple_site('1 * * * *')
    site.last_status = 'QUEUED'
    site = await site.save()
    crons = ['15 * * * *']
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0

@pytest.mark.asyncio
async def test_not_finding_sites_already_queued():
    await init_db(mock=True)
    site = simple_site('2 * * * *')
    site.last_status = 'QUEUED'
    site = await site.save()
    crons = ['2 * * * *']
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0

@pytest.mark.asyncio
async def test_not_finding_sites_disabled():
    await init_db(mock=True)
    site = simple_site('3 * * * *')
    site.disabled = True
    site = await site.save()
    crons = ['3 * * * *']
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0

@pytest.mark.asyncio
async def test_not_finding_sites_no_active_urls():
    await init_db(mock=True)
    site = simple_site('4 * * * *')
    site.base_urls[0].status = 'INACTIVE'
    site = await site.save()
    crons = ['4 * * * *']
    sites = await find_sites_eligible_for_scraping(crons).to_list()
    assert len(sites) == 0


@pytest.mark.asyncio
async def test_enqueue_scrape_task_create_scrape_task_if_not_exists():
    await init_db(mock=True)
    site = simple_site('5 * * * *')
    site = await site.save()
    site_id: PydanticObjectId = site.id # type: ignore
    site_scrape_task = await enqueue_scrape_task(site_id)
    assert site_scrape_task is not None

    second_site_scrape_task = await enqueue_scrape_task(site_id)
    assert second_site_scrape_task is None
