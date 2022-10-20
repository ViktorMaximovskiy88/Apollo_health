from datetime import datetime, timedelta

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseModel
from backend.common.models.site_scrape_task import SiteScrapeTask


class DailyCollectionStat(BaseModel):
    name: str
    updated: int
    created: int
    total: int


async def get_collection_stats(lookback_days: int) -> list[DailyCollectionStat]:
    lookback_date = datetime.today() - timedelta(days=lookback_days)
    docs = await SiteScrapeTask.aggregate(
        aggregation_pipeline=[
            {
                "$match": {
                    "start_time": {"$gte": lookback_date},
                    "status": {"$in": [TaskStatus.IN_PROGRESS, TaskStatus.FINISHED]},
                }
            },
            {"$sort": {"start_time": -1}},
            {"$group": {"_id": "$site_id", "item": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$item"}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$start_time"}},
                    "created": {"$sum": "$new_documents_found"},
                    "updated": {
                        "$sum": {"$subtract": ["$documents_found", "$new_documents_found"]}
                    },
                    "total": {"$sum": "$documents_found"},
                }
            },
            {"$addFields": {"name": "$_id"}},
        ],
        projection_model=DailyCollectionStat,
    ).to_list()

    return docs
