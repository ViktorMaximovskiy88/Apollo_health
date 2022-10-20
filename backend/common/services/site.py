from datetime import datetime, timedelta, timezone
from typing import List

from beanie import PydanticObjectId

from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
from backend.common.models.document import RetrievedDocument, UploadedDocument
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask


def find_sites_eligible_for_scraping(crons, now=datetime.now(tz=timezone.utc)):
    sites = Site.find(
        {
            "cron": {"$in": crons},  # Should be run now
            "disabled": False,  # Is active
            "status": {"$in": [SiteStatus.NEW, SiteStatus.QUALITY_HOLD, SiteStatus.ONLINE]},
            "collection_method": {"$ne": CollectionMethod.Manual},  # Isn't set to manual
            "base_urls.status": "ACTIVE",  # has at least one active url
            "$or": [
                {"last_run_time": None},  # has never been run
                {
                    "last_run_time": {"$lt": now - timedelta(minutes=1)}
                },  # hasn't been run in the last minute
            ],
            "last_run_status": {
                "$nin": [
                    TaskStatus.QUEUED,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.CANCELING,
                ]  # not already in progress
            },
        }
    )
    return sites


async def location_exists(uploaded_doc: UploadedDocument, site_id: PydanticObjectId) -> bool:
    """Check if trying to upload a doc which already exists for this site."""
    existing_docs: List[RetrievedDocument] = await RetrievedDocument.find(
        {
            "locations.site_id": site_id,
            "locations": {
                "$elemMatch": {"base_url": uploaded_doc.base_url, "url": uploaded_doc.url}
            },
        }
    ).to_list()
    if existing_docs:
        return True
    return False


async def site_last_started_task(site_id: PydanticObjectId) -> bool:
    return await SiteScrapeTask.find_one(
        {
            "site_id": site_id,
        },
        sort=[("start_time", -1)],
    )
