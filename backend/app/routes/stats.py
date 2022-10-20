from datetime import datetime, timedelta

from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.services.stats import DailyCollectionStat, get_collection_stats

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
)


def fill_data(
    lookback_days: int,
    stats: list[DailyCollectionStat],
):

    today = datetime.now()
    data = []
    for day in range(0, lookback_days):
        date_key = (today - timedelta(days=day)).strftime("%Y-%m-%d")

        stat = next(
            (d for d in stats if d.name == date_key),
            None,
        )
        data.append(
            {
                "name": date_key,
                "created": stat.created if stat else 0,
                "updated": stat.updated if stat else 0,
                "total": stat.total if stat else 0,
            }
        )

    return data


@router.get(
    "/collection",
    dependencies=[Security(get_current_user)],
)
async def collection_stats(lookback_days: int = 30):
    stats = await get_collection_stats(lookback_days)
    return fill_data(lookback_days, stats)
