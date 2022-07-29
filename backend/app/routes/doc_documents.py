from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

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
from backend.common.models.doc_document import (
    DocDocument,
    DocDocumentLimitTags,
    UpdateDocDocument,
    calc_final_effective_date,
)
from backend.common.models.user import User

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
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = DocDocument.find({}).project(DocDocumentLimitTags)
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/{id}",
    response_model=DocDocument,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_task(
    target: DocDocument = Depends(get_target),
):
    return target


@router.post("/{id}", response_model=DocDocument)
async def update_extraction_task(
    updates: UpdateDocDocument,
    target: DocDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updates.final_effective_date = calc_final_effective_date(updates)
    updated = await update_and_log_diff(logger, current_user, target, updates)

    # Sending Event Bridge Event.  Need to add condition when to send.
    document_json = EventConvert(document=updated).convert()
    send_evnt_client = SendEventClient()
    send_evnt_client.send_event("document-details", document_json)
    return updated
