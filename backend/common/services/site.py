from datetime import datetime, timedelta, timezone
from typing import List

from beanie import PydanticObjectId

from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
from backend.common.models.document import RetrievedDocument, UploadedDocument
from backend.common.models.document_mixins import get_site_location
from backend.common.models.shared import RetrievedDocumentLocation
from backend.common.models.site import Site


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
    # Check if trying to upload a doc which already exists for this site.
    existing_docs: List[RetrievedDocument] = await RetrievedDocument.find(
        {"locations.site_id": site_id}
    ).to_list()
    for existing_doc in existing_docs:
        loc: RetrievedDocumentLocation | None = get_site_location(existing_doc, site_id=site_id)
        if (
            loc.base_url == uploaded_doc.base_url
            and loc.url == uploaded_doc.url
            and loc.link_text == uploaded_doc.link_text
        ):
            return True
    return False
