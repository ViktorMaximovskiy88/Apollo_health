from fastapi import APIRouter, Security
from backend.common.models.proxy import Proxy
from backend.app.utils.user import get_current_user

router = APIRouter(
    prefix="/proxies",
    tags=["Proxies"],
)


@router.get(
    "/",
    response_model=list[Proxy],
    dependencies=[Security(get_current_user)],
)
async def read_proxies():
    proxies: list[Proxy] = await Proxy.find_many({}).to_list()
    return proxies
