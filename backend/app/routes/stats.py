import asyncio
from datetime import datetime, timedelta

from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.services.stats import docs_by_first_collected, docs_by_last_collected

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
)


def collection_recharts(
    last_collected: list[any],
    first_collected: list[any],
):

    today = datetime.now()
    data = []
    for day in range(1, 31):
        date_key = (today - timedelta(days=day)).strftime("%Y-%m-%d")

        new_doc = next(
            (d for d in first_collected if d.first_collected_date.strftime("%Y-%m-%d") == date_key),
            None,
        )
        total_doc = next(
            (d for d in last_collected if d.last_collected_date.strftime("%Y-%m-%d") == date_key),
            None,
        )

        data.append(
            {
                "name": date_key,
                "new": new_doc.count if new_doc else 0,
                "total": total_doc.count if total_doc else 0,
            }
        )

    return data


@router.get(
    "/collection",
    dependencies=[Security(get_current_user)],
)
async def report_docs_by_last_collected(lookback_days: int = 30):
    [last_collected, first_collected] = await asyncio.gather(
        docs_by_last_collected(lookback_days),
        docs_by_first_collected(lookback_days),
    )
    return collection_recharts(last_collected, first_collected)
