from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.routes.sites import Site
from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.events.event_convert import EventConvert
from backend.common.events.send_event_client import SendEventClient
from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import (
    DocDocument,
    DocDocumentLimitTags,
    DocDocumentView,
    UpdateDocDocument,
)
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.shared import DocDocumentLocationView
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.services.doc_lifecycle.hooks import doc_document_save_hook, get_doc_change_info
from backend.common.storage.text_handler import TextHandler

router = APIRouter(
    prefix="/doc-documents",
    tags=["DocDocuments"],
)


async def get_target(id: PydanticObjectId) -> DocDocument:
    task = await DocDocument.get(id)
    if not task:
        raise HTTPException(
            detail=f"Doc Document {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return task


@router.get(
    "/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_doc_documents(
    site_id: PydanticObjectId | None = None,
    scrape_task_id: PydanticObjectId | None = None,
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = {}

    if site_id:
        query["site_id"] = site_id

    if scrape_task_id:
        task = await SiteScrapeTask.get(scrape_task_id)
        if task:
            query["retrieved_document_id"] = {"$in": task.retrieved_document_ids}

    document_query = DocDocument.find(query).project(DocDocumentLimitTags)
    return await query_table(document_query, limit, skip, sorts, filters)


@router.get(
    "/{id}",
    response_model=DocDocumentView,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_task(
    target: DocDocument = Depends(get_target),
):
    # https://roman-right.github.io/beanie/tutorial/relations/
    # Only top-level fields are fully supported for now
    # cant use relations... yet...

    site_ids = [location.site_id for location in target.locations]
    sites = await Site.find({"_id": {"$in": site_ids}}).to_list()
    doc = DocDocumentView(**target.dict())

    for site in sites:
        location: DocDocumentLocationView | None = doc.get_site_location(site.id)
        if location:
            location.site_name = site.name

    return doc


class CompareResponse(BaseModel):
    diff: str
    previous_doc: DocDocument
    current_doc: DocDocument


@router.post(
    "/{id}/diff",
    response_model=CompareResponse,
    dependencies=[Security(get_current_user)],
)
async def create_diff(
    previous_doc_doc_id: PydanticObjectId, current_doc: DocDocument = Depends(get_target)
):
    text_handler = TextHandler()
    previous_doc: DocDocument = await get_target(previous_doc_doc_id)
    if current_doc.text_checksum is None or previous_doc.text_checksum is None:
        raise HTTPException(
            detail="Current or previous DocDocument does not have an associated text file.",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    _, diff = await text_handler.create_diff(previous_doc.text_checksum, current_doc.text_checksum)
    return CompareResponse(
        diff=diff.decode("utf-8"), previous_doc=previous_doc, current_doc=current_doc
    )


@router.post("/{id}", response_model=DocDocument)
async def update_doc_document(
    updates: UpdateDocDocument,
    doc: DocDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updates.final_effective_date = calc_final_effective_date(updates)
    change_info = get_doc_change_info(updates, doc)
    updated = await update_and_log_diff(logger, current_user, doc, updates)
    await doc_document_save_hook(doc, change_info)

    # Sending Event Bridge Event.  Need to add condition when to send.
    document_json = await EventConvert(document=updated).convert(doc)
    send_event_client = SendEventClient()
    send_event_client.send_event("document-details", document_json)  # noqa: F841
    return updated
