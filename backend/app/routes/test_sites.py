from datetime import datetime

from pydantic import HttpUrl
import pytest

from backend.common.db.init import init_db
from backend.common.models.site import ScrapeMethodConfiguration
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.app.routes.sites import check_for_scrapetask


class TestDeleteSite:
    def simple_site(self):
        site = Site(
            name="Test",
            scrape_method="",
            scrape_method_configuration=ScrapeMethodConfiguration(
                document_extensions=[], url_keywords=[]
            ),
            disabled=False,
            cron="5 * * * *",
            base_urls=[
                BaseUrl(
                    url=HttpUrl("https://www.example.com/", scheme="https"),
                    status="ACTIVE",
                )
            ],
        )
        return site

    def simple_scrape(
        self,
        site: Site,
    ) -> SiteScrapeTask:
        scrape = SiteScrapeTask(
            site_id=site.id,
            queued_time=datetime.now(),
        )
        return scrape

    async def populate_db(self):
        await init_db(mock=True)
        site = self.simple_site()
        await site.save()

        sites: list[Site] = []
        for i in range(3):
            site = self.simple_site()
            await site.save()
            sites.append(site)

        scrapes: list[SiteScrapeTask] = []
        for i in range(3):
            scrape = self.simple_scrape(
                sites[i % 2]
            )  # add 1st site to 2 scrapes, 2nd site to 1 scrape
            await scrape.save()
            scrapes.append(scrape)

        return scrapes, sites

    @pytest.mark.asyncio
    async def test_multiple_related_scrape_tasks(self):
        [scrapes, sites] = await self.populate_db()
        site_id = sites[0].id
        related_scrapes = await check_for_scrapetask(site_id)
        assert related_scrapes
        assert len(related_scrapes) == 2

        scrape_ids = [scrape.id for scrape in related_scrapes]
        assert scrapes[0].id in scrape_ids
        assert scrapes[1].id not in scrape_ids
        assert scrapes[2].id in scrape_ids

    @pytest.mark.asyncio
    async def test_one_related_scrape_task(self):
        [scrapes, sites] = await self.populate_db()
        site_id = sites[1].id
        related_scrapes = await check_for_scrapetask(site_id)
        assert related_scrapes
        assert len(related_scrapes) == 1

        scrape_ids = [scrape.id for scrape in related_scrapes]
        assert scrapes[0].id not in scrape_ids
        assert scrapes[1].id in scrape_ids
        assert scrapes[2].id not in scrape_ids

    @pytest.mark.asyncio
    async def test_no_related_scrape_tasks(self):
        [scrapes, sites] = await self.populate_db()
        site_id = sites[2].id
        related_scrapes = await check_for_scrapetask(site_id)
        assert not related_scrapes
        assert related_scrapes == []
