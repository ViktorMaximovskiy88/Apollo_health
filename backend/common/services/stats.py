from datetime import datetime, timedelta

from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import DocDocument


class DailyCollectionStat(BaseModel):
    name: str
    updated: int
    created: int
    total: int


async def get_collection_stats(lookback_days: int) -> list[DailyCollectionStat]:
    lookback_date = datetime.today() - timedelta(days=lookback_days)
    docs = await DocDocument.aggregate(
        aggregation_pipeline=[
            {
                "$match": {
                    "start_time": {"$gte": lookback_date},
                }
            },
            {"$sort": {"start_time": -1}},
            {"$group": {"_id": "$site_id", "item": {"$first": "$$ROOT"}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$start_time"}},
                    "count": {"$sum": 1},
                }
            },
            {"$addFields": {"name": "$_id"}},
        ],
        projection_model=DailyCollectionStat,
    ).to_list()

    return docs
