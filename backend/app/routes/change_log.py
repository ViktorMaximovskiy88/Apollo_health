from fastapi import APIRouter, Security
from bson import ObjectId

from backend.common.models.change_log import ChangeLog
from backend.common.models.user import User
from backend.app.utils.user import get_current_user
from backend.app.utils.auth0 import auth0

router = APIRouter(
    prefix="/change-log",
    tags=["ChangeLog"],
)


@router.get("/{id}", response_model=list[ChangeLog])
async def get_changes_for_id(
    id: str,
    current_user = Security(auth0.get_current_user, scopes=["profile", "asd"]),
) -> list[ChangeLog]:
    logs = (
        await ChangeLog.find(ChangeLog.target_id == ObjectId(id)).sort("id").to_list()
    )
    return logs
