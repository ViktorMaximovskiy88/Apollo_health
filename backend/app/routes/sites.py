import urllib.parse

from beanie import PydanticObjectId
from beanie.operators import ElemMatch
from fastapi import APIRouter, Depends, HTTPException, Query, Security, UploadFile, status

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    _prepare_table_query,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.uploads import get_sites_from_upload
from backend.app.utils.user import get_current_user
from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
from backend.common.models.doc_document import DocDocument, SiteDocDocument
from backend.common.models.document import (
    RetrievedDocument,
    RetrievedDocumentLimitTags,
    SiteRetrievedDocument,
)
from backend.common.models.site import (
    ActiveUrlResponse,
    NewSite,
    Site,
    UpdateSite,
    UpdateSiteAssigne,
)
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.services.collection import CollectionService
from backend.common.services.doc_document import get_site_doc_doc_table

router = APIRouter(
    prefix="/sites",
    tags=["Sites"],
)


async def get_target(site_id: PydanticObjectId) -> Site:
    site = await Site.get(site_id)
    if not site:
        raise HTTPException(
            detail=f"Site {site_id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
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


@router.get(
    "/search",
    dependencies=[Security(get_current_user)],
    response_model=Site,
)
async def read_site_by_name(
    name: str,
):
    site = await Site.find_one({"name": name})
    return site


@router.get("/{site_id}", response_model=Site, dependencies=[Security(get_current_user)])
async def read_site(
    target: Site = Depends(get_target),
):
    return target


@router.put("/", response_model=Site, status_code=status.HTTP_201_CREATED)
async def create_site(
    site: NewSite,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Site:
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


@router.post("/bulk-assign")
async def update_multiple_sites(
    updates: list[UpdateSiteAssigne],
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    site_ids: list[PydanticObjectId] = [update.id for update in updates]
    targets: list[Site] = await Site.find_many({"_id": {"$in": site_ids}}).to_list()
    result = []

    for target in targets:
        updated = await update_and_log_diff(
            logger, current_user, target, UpdateSite(assignee=current_user.id)
        )
        result.append(updated)

    return result


@router.post("/{site_id}", response_model=Site)
async def update_site(
    updates: UpdateSite,
    target: Site = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    original_collection_method: str | None = (
        target.collection_method if target.collection_method else None
    )
    updated = await update_and_log_diff(logger, current_user, target, updates)
    updated_collection_method = updated.get("collection_method", False)

    # If site was automated but then switched to manual,
    # stop manual tasks just in case pending work items are stuck in queue.
    if (
        updated_collection_method
        and updated_collection_method == CollectionMethod.Manual
        and original_collection_method != CollectionMethod.Manual
    ):
        site_collection: CollectionService = CollectionService(
            site=target,
            current_user=current_user,
            logger=logger,
        )
        await site_collection.stop_manual()

    return updated


@router.delete(
    "/{site_id}",
    responses={
        405: {"description": "Item can't be deleted because of associated collection records."},
    },
)
async def delete_site(
    target: Site = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
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
    scrape_task_id: PydanticObjectId | None = None,
):
    query = {"locations.site_id": site_id}
    if scrape_task_id:
        scrape_task: SiteScrapeTask | None = await SiteScrapeTask.get(scrape_task_id)
        if not scrape_task:
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                f"Scrape Task {scrape_task_id} does not exist",
            )
        query["_id"] = {"$in": scrape_task.retrieved_document_ids}

    docs = (
        await RetrievedDocument.find(query)
        .sort("-first_collected_date")
        .project(RetrievedDocumentLimitTags)
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
    doc: RetrievedDocument | None = await RetrievedDocument.find_one(
        {"_id": doc_id, "locations.site_id": site_id}
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return doc.for_site(site_id)


@router.get(
    "/{site_id}/doc-documents",
    dependencies=[Security(get_current_user)],
)
async def get_site_doc_docs(
    site_id: PydanticObjectId,
    site: Site = Depends(get_target),
    scrape_task_id: PydanticObjectId | None = None,
    limit: int = 50,
    skip: int = 0,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    current_task: SiteScrapeTask | None = await SiteScrapeTask.find_one(
        {
            "site_id": site_id,
            "status": {"$in": CollectionService.queued_statuses},
        },
        sort=[("start_time", -1)],
    )

    (match_filter, sort_by) = _prepare_table_query(sorts, filters)

    retrieved_document_ids = []
    if current_task and current_task.collection_method == CollectionMethod.Manual:
        retrieved_document_ids = current_task.retrieved_document_ids
    elif scrape_task_id:
        scrape_task: SiteScrapeTask | None = await SiteScrapeTask.get(scrape_task_id)
        if scrape_task and scrape_task.status != TaskStatus.CANCELED:
            retrieved_document_ids = scrape_task.retrieved_document_ids

    data, total = await get_site_doc_doc_table(
        site_id,
        retrieved_document_ids=retrieved_document_ids,
        filters=match_filter,
        sorts=sort_by,
        limit=limit,
        skip=skip,
    )
    return TableQueryResponse(data=data, total=total)


@router.get(
    "/{site_id}/doc-documents/{doc_id}",
    response_model=SiteDocDocument,
    dependencies=[Security(get_current_user)],
)
async def get_site_doc_doc_by_id(
    site_id: PydanticObjectId,
    doc_id: PydanticObjectId,
):
    doc = await DocDocument.find_one({"_id": doc_id, "locations.site_id": site_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return doc.for_site(site_id)
