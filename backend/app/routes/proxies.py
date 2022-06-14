from fastapi import APIRouter, Depends
from backend.common.models.proxy import Proxy
from backend.common.models.user import User
from backend.app.utils.user import get_current_user

router = APIRouter(
    prefix="/proxies",
    tags=["Proxies"],
)

@router.get("/", response_model=list[Proxy])
async def read_proxies(
    current_user: User = Depends(get_current_user),
):
    proxies: list[Proxy] = await Proxy.find_many({}).to_list()
    return proxies
