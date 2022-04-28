from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from backend.common.models.site import NewSite, Site, UpdateSite
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user

router = APIRouter(
    prefix="/sites",
    tags=["Sites"],
)


async def get_target(id: PydanticObjectId):
    user = await Site.get(id)
    if not user:
        raise HTTPException(
            detail=f"Site {id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return user


@router.get("/", response_model=list[Site])
async def read_sites(
    current_user: User = Depends(get_current_user),
):
    sites: list[Site] = await Site.find_many({}).to_list()
    sites.reverse()
    return sites


@router.get("/{id}", response_model=Site)
async def read_site(
    target: User = Depends(get_target),
    current_user: User = Depends(get_current_user),
):
    return target


@router.put("/", response_model=Site, status_code=status.HTTP_201_CREATED)
async def create_site(
    site: NewSite,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_site = Site(
        name=site.name,
        base_url=site.base_url,
        scrape_method=site.scrape_method,
        tags=site.tags,
        disabled=False,
        cron=site.cron,
    )
    await create_and_log(logger, current_user, new_site)
    return new_site


@router.post("/{id}", response_model=Site)
async def update_site(
    updates: UpdateSite,
    target: Site = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_site(
    target: Site = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UpdateSite(disabled=True))
    return {"success": True}
