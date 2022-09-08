from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Security, status

from backend.app.utils.user import get_current_user
from backend.common.models.app_config import AppConfig

router = APIRouter(
    prefix="/app-config",
    tags=["AppConfig"],
)


async def get_target(id: PydanticObjectId):
    user = await AppConfig.get(id)
    if not user:
        raise HTTPException(
            detail=f"App Config {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return user


@router.get("/", response_model=AppConfig, dependencies=[Security(get_current_user)])
async def get_config(key: str):
    app_config = await AppConfig.find_one({"key": key})
    if not app_config:
        raise HTTPException(
            detail=f"App Config {key} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return app_config
