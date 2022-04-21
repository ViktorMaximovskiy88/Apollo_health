from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument

from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.storage.client import DocumentStorageClient

router = APIRouter(
    prefix="/documents",
    tags=["Dcouments"],
)


async def get_target(id: PydanticObjectId):
    doc = await RetrievedDocument.get(id)
    if not doc:
        raise HTTPException(
            detail=f"Retrieved Document {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return doc


@router.get("/", response_model=list[RetrievedDocument])
async def read_documents(
    scrape_task_id: PydanticObjectId | None = None,
    site_id: PydanticObjectId | None = None,
    logical_document_id: PydanticObjectId | None = None,
    current_user: User = Depends(get_current_user),
):
    query = {}
    if site_id:
        query[RetrievedDocument.site_id] = site_id
    if scrape_task_id:
        query[RetrievedDocument.scrape_task_id] = scrape_task_id
    if logical_document_id:
        query[RetrievedDocument.logical_document_id] = logical_document_id

    documents: list[RetrievedDocument] = (
        await RetrievedDocument.find_many(query).sort("-collection_time").to_list()
    )
    return documents


@router.get("/{id}.pdf")
async def download_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Depends(get_current_user),
):
    client = DocumentStorageClient()
    return StreamingResponse(client.read_document_stream(f"{target.checksum}.pdf"))


@router.get("/{id}", response_model=RetrievedDocument)
async def read_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: RetrievedDocument = Depends(get_current_user),
):
    return target


@router.put("/", response_model=RetrievedDocument, status_code=status.HTTP_201_CREATED)
async def add_document(
    site_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    site_scrape_task = RetrievedDocument(site_id=site_id)
    await create_and_log(logger, current_user, site_scrape_task)
    return site_scrape_task


@router.post("/{id}", response_model=RetrievedDocument)
async def update_document(
    updates: UpdateRetrievedDocument,
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(
        logger, current_user, target, UpdateRetrievedDocument(disabled=True)
    )
    return {"success": True}
