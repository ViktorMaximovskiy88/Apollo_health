from fastapi import APIRouter, Security
from bson import ObjectId

from backend.common.models.change_log import ChangeLog
from backend.app.utils.user import get_current_user

router = APIRouter(
    prefix="/change-log",
    tags=["ChangeLog"],
)


@router.get(
    "/{id}",
    response_model=list[ChangeLog],
    dependencies=[Security(get_current_user)],
)
async def get_changes_for_id(
    id: str,
) -> list[ChangeLog]:
    logs = (
        await ChangeLog.find(ChangeLog.target_id == ObjectId(id)).sort("id").to_list()
    )

    return logs
