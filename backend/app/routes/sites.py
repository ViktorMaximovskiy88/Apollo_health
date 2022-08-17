import urllib.parse

from beanie import PydanticObjectId
from beanie.operators import ElemMatch
from fastapi import APIRouter, Depends, HTTPException, Query, Security, UploadFile, status

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.uploads import get_sites_from_upload
from backend.app.utils.user import get_current_user
from backend.common.core.enums import SiteStatus
from backend.common.models.document import (
    RetrievedDocument,
    RetrievedDocumentLimitTags,
    SiteRetrievedDocument,
)
from backend.common.models.site import ActiveUrlResponse, NewSite, Site, UpdateSite
from backend.common.models.user import User

from ...common.models.doc_document import DocDocument, DocDocumentLimitTags, SiteDocDocument

router = APIRouter(
    prefix="/sites",
    tags=["Sites"],
)


async def get_target(id: PydanticObjectId) -> Site:
    site = await Site.get(id)
    if not site:
        raise HTTPException(detail=f"Site {id} Not Found", status_code=status.HTTP_404_NOT_FOUND)
    return site


@router.get("/", response_model=TableQueryResponse, dependencies=[Security(get_current_user)])
async def read_sites(
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = Site.find({"disabled": False})
    return await query_table(query, limit, skip, sorts, filters)


@router.get("/download", response_model=list[NewSite], dependencies=[Security(get_current_user)])
async def download_sites():
    return (
        await Site.find({"disabled": False, "status": {"$ne": SiteStatus.INACTIVE}})
        .project(NewSite)
        .to_list()
    )


@router.get(
    "/active-url",
    response_model=ActiveUrlResponse,
    dependencies=[Security(get_current_user)],
)
async def check_url(
    url: str,
    current_site: PydanticObjectId | None = Query(default=None, alias="currentSite"),
):
    site = await Site.find_one(
        ElemMatch(Site.base_urls, {"url": urllib.parse.unquote(url)}),
        Site.id != current_site,
        {"disabled": False},
    )

    if site:
        return ActiveUrlResponse(in_use=True, site=site)
    else:
        return ActiveUrlResponse(in_use=False)


@router.get("/{id}", response_model=Site, dependencies=[Security(get_current_user)])
async def read_site(
    target: Site = Depends(get_target),
):
    return target


@router.put("/", response_model=Site, status_code=status.HTTP_201_CREATED)
async def create_site(
    site: NewSite,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_site = Site(
        name=site.name,
        creator_id=current_user.id,
        base_urls=site.base_urls,
        scrape_method=site.scrape_method,
        collection_method=site.collection_method,
        scrape_method_configuration=site.scrape_method_configuration,
        tags=site.tags,
        disabled=False,
        cron=site.cron,
    )
    await create_and_log(logger, current_user, new_site)
    return new_site


@router.post("/upload", response_model=list[Site])
async def upload_sites(
    file: UploadFile,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_sites: list[Site] = []
    for new_site in get_sites_from_upload(file):
        if await Site.find_one(Site.base_urls == new_site.base_urls):
            continue
        if new_site.base_urls:
            new_sites.append(new_site)
            await create_and_log(logger, current_user, new_site)

    return new_sites


@router.post("/{id}", response_model=Site)
async def update_site(
    updates: UpdateSite,
    target: Site = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete(
    "/{id}",
    responses={
        405: {"description": "Item can't be deleted because of associated collection records."},
    },
)
async def delete_site(
    id: PydanticObjectId,
    target: Site = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    # check for associated collection records, return error if present
    # - reimplement check at later date.
    # scrape_task = await SiteScrapeTask.find_many({"site_id": site_id}).to_list()
    scrape_task = False
    if scrape_task:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Sites with run collections cannot be deleted.",
        )

    await update_and_log_diff(logger, current_user, target, UpdateSite(disabled=True))
    return {"success": True}


@router.get(
    "/{site_id}/documents",
    response_model=list[SiteRetrievedDocument],
    dependencies=[Security(get_current_user)],
)
async def get_site_docs(
    site_id: PydanticObjectId,
):
    docs = (
        await RetrievedDocument.find({"locations.site_id": site_id})
        .project(RetrievedDocumentLimitTags)
        .to_list()
    )
    return [doc.for_site(site_id) for doc in docs]


@router.get(
    "/{site_id}/doc-documents",
    response_model=list[SiteDocDocument],
    dependencies=[Security(get_current_user)],
)
async def get_site_doc_docs(
    site_id: PydanticObjectId,
):
    docs = (
        await DocDocument.find({"locations.site_id": site_id})
        .project(DocDocumentLimitTags)
        .to_list()
    )
    return [doc.for_site(site_id) for doc in docs]


@router.get(
    "/{site_id}/documents/{doc_id}",
    response_model=SiteRetrievedDocument,
    dependencies=[Security(get_current_user)],
)
async def get_site_doc_by_id(
    site_id: PydanticObjectId,
    doc_id: PydanticObjectId,
):
    doc = await RetrievedDocument.find_one({"_id": doc_id, "locations.site_id": site_id}).project(
        RetrievedDocumentLimitTags
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return doc.for_site(site_id)
