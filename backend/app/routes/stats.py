import asyncio
from datetime import datetime, timedelta

from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.services.stats import (
    FirstCollectionStats,
    LastCollectionStats,
    get_created_docs,
    get_updated_docs,
)

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
)


def collection_recharts(
    lookback_days: int,
    created_docs: list[FirstCollectionStats],
    updated_docs: list[LastCollectionStats],
):

    today = datetime.now()
    data = []
    for day in range(0, lookback_days):
        date_key = (today - timedelta(days=day)).strftime("%Y-%m-%d")

        created_doc = next(
            (d for d in created_docs if d.first_collected_date.strftime("%Y-%m-%d") == date_key),
            None,
        )
        updated_doc = next(
            (d for d in updated_docs if d.last_collected_date.strftime("%Y-%m-%d") == date_key),
            None,
        )

        data.append(
            {
                "name": date_key,
                "created": created_doc.count if created_doc else 0,
                "updated": updated_doc.count if updated_doc else 0,
            }
        )

    return data


@router.get(
    "/collection",
    dependencies=[Security(get_current_user)],
)
async def collection_stats(lookback_days: int = 30):
    [created_docs, updated_docs] = await asyncio.gather(
        get_created_docs(lookback_days),
        get_updated_docs(lookback_days),
    )
    return collection_recharts(lookback_days, created_docs, updated_docs)
