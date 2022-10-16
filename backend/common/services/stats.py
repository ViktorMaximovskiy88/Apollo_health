from datetime import date, datetime, timedelta

from pydantic import BaseModel

from backend.common.models.doc_document import DocDocument


class LastCollectionStats(BaseModel):
    last_collected_date: date
    count: int


class FirstCollectionStats(BaseModel):
    first_collected_date: date
    count: int


async def docs_by_last_collected(lookback_days: int) -> list[LastCollectionStats]:
    lookback_date = datetime.today() - timedelta(days=lookback_days)
    docs = await DocDocument.aggregate(
        aggregation_pipeline=[
            {"$match": {"last_collected_date": {"$gte": lookback_date}}},
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


async def docs_by_first_collected(lookback_days: int) -> list[FirstCollectionStats]:
    lookback_date = datetime.today() - timedelta(days=lookback_days)
    docs = await DocDocument.aggregate(
        aggregation_pipeline=[
            {"$match": {"first_collected_date": {"$gte": lookback_date}}},
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
