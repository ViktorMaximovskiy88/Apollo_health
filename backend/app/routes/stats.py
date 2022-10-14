from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.services.stats import StatCount, docs_by_last_collected

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
)


@router.get(
    "/last-collected",
    dependencies=[Security(get_current_user)],
    response_model=list[StatCount],
)
async def report_docs_by_last_collected(lookback_days: int = 30):
    docs = await docs_by_last_collected(lookback_days)
    return docs
