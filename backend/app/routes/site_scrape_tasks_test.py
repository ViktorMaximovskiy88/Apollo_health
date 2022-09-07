from datetime import datetime, timedelta, timezone
from random import random

import pytest
import pytest_asyncio
from beanie import Document
from fastapi import HTTPException

from backend.app.routes.site_scrape_tasks import (
    BulkRunResponse,
    cancel_scrape_task,
    run_bulk_by_type,
    start_scrape_task,
)
from backend.common.core.enums import BulkScrapeActions, CollectionMethod, SiteStatus, TaskStatus
from backend.common.db.init import init_db
from backend.common.models.site import BaseUrl, HttpUrl, ScrapeMethodConfiguration, Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture()
@pytest.mark.asyncio()
async def user():
    user = User(
        id="62e7c6647e2a94f469d57f34",
        email="example@me.com",
        full_name="John Doe",
        hashed_password="example",
    )
    await user.save()

    return user


class MockLogger:
    async def background_log_change(
        self, current_user: User, site_scrape_task: Document, action: str
    ):
        assert current_user.id is not None
        assert type(action) == str
        return None


@pytest_asyncio.fixture()
async def logger():
    return MockLogger()


def simple_site(
    disabled=False,
    base_urls=[BaseUrl(url=HttpUrl("https://www.example.com/", scheme="https"), status="ACTIVE")],
    collection_method=CollectionMethod.Automated,
    collection_hold=None,
    status=SiteStatus.ONLINE,
    last_run_status=None,
) -> Site:
    return Site(
        name="Test",
        collection_method=collection_method,
        collection_hold=collection_hold,
        scrape_method="",
        scrape_method_configuration=ScrapeMethodConfiguration(
            document_extensions=[],
            url_keywords=[],
            proxy_exclusions=[],
            follow_links=False,
            follow_link_keywords=[],
            follow_link_url_keywords=[],
        ),
        disabled=disabled,
        last_run_status=last_run_status,
        status=status,
        cron="0 * * * *",
        base_urls=base_urls,
    )


def simple_scrape(site: Site, status=TaskStatus.QUEUED) -> SiteScrapeTask:
    return SiteScrapeTask(
        site_id=site.id,
        status=status,
        queued_time=datetime.now(tz=timezone.utc),
    )


class TestStartScrapeTask:
    @pytest.mark.asyncio
    async def test_run_collection(self, user, logger):
        site_one = await simple_site().save()

        res = await start_scrape_task(site_one.id, user, logger)
        assert res.site_id == site_one.id
        scrapes = await SiteScrapeTask.find({}).to_list()
        assert len(scrapes) == 1
        update_site = await Site.find_one({})
        assert update_site.last_run_status == res.status == TaskStatus.QUEUED

    async def test_no_site_found(self, user, logger):
        with pytest.raises(HTTPException) as e:
            await start_scrape_task("62e823397ab9edcd2557612d", user, logger)
        assert isinstance(e.value, HTTPException)
        assert e.value.status_code == 404
        assert e.value.detail == "Site 62e823397ab9edcd2557612d Not Found"
        scrapes = await SiteScrapeTask.find({}).to_list()
        assert len(scrapes) == 0

    @pytest.mark.asyncio
    async def test_already_scraping(self):
        site_one = await simple_site().save()
        scrape_one = await simple_scrape(site_one).save()
        site_two = await simple_site().save()
        scrape_two = await simple_scrape(site_two, TaskStatus.IN_PROGRESS).save()

        with pytest.raises(HTTPException) as e:
            await start_scrape_task(site_one.id, user, logger)
        assert isinstance(e.value, HTTPException)
        assert e.value.status_code == 406
        assert e.value.detail == f"Scrapetask {scrape_one.id} is already queued or in progress."
        scrapes = await SiteScrapeTask.find({}).to_list()
        assert len(scrapes) == 2

        with pytest.raises(HTTPException) as e:
            await start_scrape_task(site_two.id, user, logger)
        assert isinstance(e.value, HTTPException)
        assert e.value.status_code == 406
        assert e.value.detail == f"Scrapetask {scrape_two.id} is already queued or in progress."
        scrapes = await SiteScrapeTask.find({}).to_list()
        assert len(scrapes) == 2


class TestRunBulk:
    @pytest.mark.asyncio
    async def test_run_unrun(self, user, logger):
        site_one = await simple_site(status=SiteStatus.NEW).save()
        await simple_site(last_run_status=TaskStatus.FAILED).save()

        res = await run_bulk_by_type("new", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.RUN, scrapes=1, sites=1)
        scrape = await SiteScrapeTask.find({"site_id": site_one.id}).count()
        assert scrape == 1

    @pytest.mark.asyncio
    async def test_run_failed(self, user, logger):
        site_one = await simple_site(last_run_status=TaskStatus.FAILED).save()
        site_two = await simple_site(last_run_status=TaskStatus.CANCELED).save()
        await simple_site().save()

        res = await run_bulk_by_type("failed", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.RUN, scrapes=2, sites=2)
        scrapes = await SiteScrapeTask.find(
            {"site_id": {"$in": [site_one.id, site_two.id]}}
        ).count()
        assert scrapes == 2

    @pytest.mark.asyncio
    async def test_run_canceled(self, user, logger):
        site_one = await simple_site(last_run_status=TaskStatus.CANCELED).save()
        await simple_site().save()

        res = await run_bulk_by_type("failed", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.RUN, scrapes=1, sites=1)
        scrapes = await SiteScrapeTask.find({"site_id": site_one.id}).count()
        assert scrapes == 1

    @pytest.mark.asyncio
    async def test_run_all(self, user, logger):
        site_one = await simple_site().save()
        await simple_site(last_run_status=TaskStatus.QUEUED).save()
        await simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()

        res = await run_bulk_by_type("all", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.RUN, scrapes=1, sites=1)
        scrapes = await SiteScrapeTask.find({"site_id": site_one.id}).count()
        assert scrapes == 1

    @pytest.mark.asyncio
    async def test_run_no_scrapes(self, user, logger):
        sites: list[Site] = []
        sites.append(simple_site(disabled=True))
        sites.append(simple_site(base_urls=[]))
        sites.append(simple_site(collection_method=CollectionMethod.Manual))
        sites.append(simple_site(status=SiteStatus.INACTIVE))
        await Site.insert_many(sites)

        bulk_types = ["unrun", "failed", "canceled", "all"]
        for bulk_type in bulk_types:
            res = await run_bulk_by_type(bulk_type, logger=logger, current_user=user)
            assert res == BulkRunResponse(type=BulkScrapeActions.RUN, scrapes=0, sites=0)

        scrapes = await SiteScrapeTask.find({}).count()
        assert scrapes == 0

    @pytest.mark.asyncio
    async def test_cancel_active(self, user, logger):
        site_one = await simple_site(
            status=SiteStatus.INACTIVE, last_run_status=TaskStatus.QUEUED
        ).save()
        site_two = await simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()
        site_three = await simple_site().save()
        await simple_scrape(site_one).save()
        await simple_scrape(site_two).save()
        scrape_one = await simple_scrape(site_three).save()

        res = await run_bulk_by_type("cancel-active", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.CANCEL, sites=2, scrapes=2)
        canceled_scrapes = await SiteScrapeTask.find({"status": TaskStatus.CANCELING}).count()
        assert canceled_scrapes == 2
        active_scrapes = await SiteScrapeTask.find({"status": TaskStatus.QUEUED}).to_list()
        assert len(active_scrapes) == 1
        assert active_scrapes[0].id == scrape_one.id

    @pytest.mark.asyncio
    async def test_cancel_no_scrapes(self, user, logger):
        site_one = await simple_site().save()
        await simple_scrape(site_one).save()

        res = await run_bulk_by_type("cancel-active", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.CANCEL, sites=0, scrapes=0)
        scrapes = await SiteScrapeTask.find({"status": TaskStatus.CANCELED}).count()
        assert scrapes == 0

    @pytest.mark.asyncio
    async def test_hold_all(self, user, logger):
        site_one = await simple_site(last_run_status=TaskStatus.QUEUED).save()
        await simple_scrape(site_one).save()
        await simple_site().save()
        tomorrow = datetime.now() + timedelta(days=1)

        res = await run_bulk_by_type("hold-all", logger=logger, current_user=user)
        assert res == BulkRunResponse(type=BulkScrapeActions.HOLD, sites=2, scrapes=1)
        scrapes = await SiteScrapeTask.find(
            {"status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}}
        ).count()
        assert scrapes == 0
        sites = await Site.find_all().to_list()
        for site in sites:
            if site.id == site_one.id:
                assert site.last_run_status == TaskStatus.CANCELING
            else:
                assert site.last_run_status is None

            assert site.collection_hold is not None
            assert site.collection_hold >= tomorrow

    @pytest.mark.asyncio
    async def test_cancel_hold_all(self, user, logger):
        now = datetime.now(tz=timezone.utc)
        for i in range(0, 2):
            site = simple_site(collection_hold=now)
            await site.save()
        await simple_site().save()

        res = await run_bulk_by_type("cancel-hold-all", logger=logger, current_user=user)
        assert res.type == BulkScrapeActions.CANCEL_HOLD
        assert res.sites == 2
        sites = await Site.find({"collection_hold": None}).count()
        assert sites == 3


class TestCancel:
    @pytest.mark.asyncio
    async def test_cancel_queued(self):
        site_one = await simple_site(last_run_status=TaskStatus.QUEUED).save()
        await simple_site(last_run_status=TaskStatus.QUEUED).save()
        scrape_one = await simple_scrape(site_one).save()
        await simple_scrape(site_one).save()

        res = await cancel_scrape_task(scrape_one)
        assert res.id == scrape_one.id
        scrape = await SiteScrapeTask.find({"status": TaskStatus.CANCELED}).to_list()
        assert len(scrape) == 1
        assert scrape[0].id == scrape_one.id
        site = await Site.find({"last_run_status": TaskStatus.CANCELED}).to_list()
        assert len(site) == 1
        assert site[0].id == site_one.id

    @pytest.mark.asyncio
    async def test_cancel_in_progress(self):
        site_one = await simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()
        await simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()
        scrape_one = await simple_scrape(site_one, TaskStatus.IN_PROGRESS).save()
        await simple_scrape(site_one, TaskStatus.IN_PROGRESS).save()

        res = await cancel_scrape_task(scrape_one)
        assert res.id == scrape_one.id
        scrape = await SiteScrapeTask.find({"status": TaskStatus.CANCELING}).to_list()
        assert len(scrape) == 1
        assert scrape[0].id == scrape_one.id
        site = await Site.find({"last_run_status": TaskStatus.CANCELING}).to_list()
        assert len(site) == 1
        assert site[0].id == site_one.id

    @pytest.mark.asyncio
    async def test_cancel_fail(self):
        site_one = await simple_site(last_run_status=TaskStatus.FINISHED).save()
        await simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()
        scrape_one = await simple_scrape(site_one, TaskStatus.FINISHED).save()
        await simple_scrape(site_one, TaskStatus.IN_PROGRESS).save()

        with pytest.raises(HTTPException) as e:
            await cancel_scrape_task(scrape_one)
        assert isinstance(e.value, HTTPException)
        assert e.value.status_code == 406
        assert e.value.detail == "Scrape task is not queued or in progress."

        scrape = await SiteScrapeTask.find(
            {"status": {"$in": [TaskStatus.CANCELING, TaskStatus.CANCELED]}}
        ).to_list()
        assert len(scrape) == 0
        site = await Site.find(
            {"last_run_status": {"$in": [TaskStatus.CANCELING, TaskStatus.CANCELED]}}
        ).to_list()
        assert len(site) == 0
