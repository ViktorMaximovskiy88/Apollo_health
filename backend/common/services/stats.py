from datetime import date, datetime, timedelta

from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import DocDocument


class LastCollectionStats(BaseModel):
    last_collected_date: date
    count: int


class FirstCollectionStats(BaseModel):
    first_collected_date: date
    count: int


async def get_updated_docs(lookback_days: int) -> list[LastCollectionStats]:
    lookback_date = datetime.today() - timedelta(days=lookback_days)
    docs = await DocDocument.aggregate(
        aggregation_pipeline=[
            {
                "$match": {
                    "last_collected_date": {"$gte": lookback_date},
                    "$expr": {"$ne": ["$last_collected_date", "$first_collected_date"]},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$last_collected_date"}
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$addFields": {"last_collected_date": "$_id"}},
            {"$sort": {"_id": -1}},
        ],
        projection_model=LastCollectionStats,
    ).to_list()

    return docs


async def get_created_docs(lookback_days: int) -> list[FirstCollectionStats]:
    lookback_date = datetime.today() - timedelta(days=lookback_days)
    docs = await DocDocument.aggregate(
        aggregation_pipeline=[
            {
                "$match": {
                    "first_collected_date": {"$gte": lookback_date},
                    "$expr": {"$eq": ["$last_collected_date", "$first_collected_date"]},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$first_collected_date"}
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$addFields": {"first_collected_date": "$_id"}},
            {"$sort": {"_id": -1}},
        ],
        projection_model=FirstCollectionStats,
    ).to_list()

    return docs
