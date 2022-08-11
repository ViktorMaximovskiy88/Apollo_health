from datetime import datetime, timedelta, timezone

from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
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
