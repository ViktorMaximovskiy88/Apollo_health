import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask


async def rectify_last_scrape_data():
    async for site in Site.find_all():
        scrape_task = (
            await SiteScrapeTask.find({"site_id": site.id}).sort("-queued_time").first_or_none()
        )
        if not scrape_task:
            continue

        if site.last_run_status != scrape_task.status:
            print(site.id, site.name, site.last_run_status, scrape_task.status)
            await Site.get_motor_collection().update_one(
                {"_id": site.id}, {"$set": {"last_run_status": scrape_task.status}}
            )


async def execute():
    await init_db()
    await rectify_last_scrape_data()


if __name__ == "__main__":
    asyncio.run(execute())
