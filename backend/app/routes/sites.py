import io
import pymongo
import urllib.parse
import zipfile
from beanie import PydanticObjectId
from beanie.operators import ElemMatch
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from openpyxl import load_workbook
from pydantic import BaseModel

from backend.common.models.site import (
    NewSite,
    ScrapeMethodConfiguration,
    Site,
    UpdateSite,
)
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
    sites: list[Site] = await Site.find_many({}).sort("-last_run_time", "id").to_list()
    return sites


class ActiveUrlResponse(BaseModel):
    in_use: bool
    site: Site | None = None


@router.get("/active-url", response_model=ActiveUrlResponse)
async def check_url(
    url: str,
    current_site: str | None = Query(default=None, alias="currentSite"),
    current_user: User = Depends(get_current_user),
):
    site: Site = await Site.find_one(
        ElemMatch(Site.base_urls, {"url": urllib.parse.unquote(url)}),
        Site.id != PydanticObjectId(current_site),
        Site.disabled != True
    )

    if site:
        return ActiveUrlResponse(in_use=True, site=site)
    else:
        return ActiveUrlResponse(in_use=False)


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
        base_urls=site.base_urls,
        scrape_method=site.scrape_method,
        scrape_method_configuration=site.scrape_method_configuration,
        tags=site.tags,
        disabled=False,
        cron=site.cron,
    )
    await create_and_log(logger, current_user, new_site)
    return new_site


def get_lines_from_xlsx(file: UploadFile):
    wb = load_workbook(io.BytesIO(file.file.read()))
    sheet = wb[wb.sheetnames[0]]
    for i, line in enumerate(sheet.values):
        if i == 0:
            continue  # skip header
        yield line


def get_lines_from_text_file(file: UploadFile):
    for line in file.file:
        line = line.decode("utf-8").strip()
        name, base_urls, scrape_method, tags, cron = line.split("\t")
        yield (name, base_urls, scrape_method, tags, cron)


def get_lines_from_upload(file: UploadFile):
    try:
        return get_lines_from_xlsx(file)
    except zipfile.BadZipFile:
        return get_lines_from_text_file(file)


@router.post("/upload", response_model=list[Site])
async def upload_sites(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_sites = []
    for line in get_lines_from_upload(file):
        name, base_urls, scrape_method, tags, cron: (str, str, str, str, str) = line  # type: ignore
        tags = tags.split(",") if tags else []
        base_urls = base_urls.split(",") if base_urls else []
        scrape_method_configuration = ScrapeMethodConfiguration(
            document_extensions=[], url_keywords=[]
        )

        if await Site.find_one(Site.base_urls == base_urls):
            continue

        new_site = Site(
            name=name,
            base_urls=base_urls,
            scrape_method=scrape_method,
            scrape_method_configuration=scrape_method_configuration,
            tags=tags,
            disabled=False,
            cron=cron,
        )
        new_sites.append(new_site)
        await create_and_log(logger, current_user, new_site)

    return new_sites


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
