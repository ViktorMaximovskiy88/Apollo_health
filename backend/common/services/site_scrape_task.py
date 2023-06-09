from beanie import PydanticObjectId

from backend.common.models.site_scrape_task import SiteScrapeTask


async def check_for_scrapetask(site_id: PydanticObjectId) -> list[SiteScrapeTask]:
    scrape_task = await SiteScrapeTask.find_many({"site_id": site_id}).to_list()
    return scrape_task


async def get_many_for_doc(doc_id: PydanticObjectId) -> list[SiteScrapeTask]:
    scrape_task = await SiteScrapeTask.find_many({"retreived_doc_ids": doc_id}).to_list()
    return scrape_task
