from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.storage.client import ModelStorageClient

router = APIRouter(
    prefix="/therapy-master",
    tags=["Therapy Master"],
)


@router.get(
    "/upload",
    dependencies=[Security(get_current_user)],
)
async def get_upload_url(version: str):
    client = ModelStorageClient()
    url = client.get_signed_upload_url(f"upload/{version}.zip")
    return {"url": url}
