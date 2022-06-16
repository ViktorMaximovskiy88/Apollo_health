from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import StreamingResponse
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument

from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.security import backend
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


@router.get(
    "/",
    response_model=list[RetrievedDocument],
    dependencies=[Security(backend.get_current_user)],
)
async def read_documents(
    scrape_task_id: PydanticObjectId | None = None,
    site_id: PydanticObjectId | None = None,
    logical_document_id: PydanticObjectId | None = None,
    automated_content_extraction: bool | None = None,
):
    query = {}
    if site_id:
        query[RetrievedDocument.site_id] = site_id
    if scrape_task_id:
        query[RetrievedDocument.scrape_task_id] = scrape_task_id
    if logical_document_id:
        query[RetrievedDocument.logical_document_id] = logical_document_id
    if automated_content_extraction:
        query[
            RetrievedDocument.automated_content_extraction
        ] = automated_content_extraction

    documents: list[RetrievedDocument] = (
        await RetrievedDocument.find_many(query).sort("-collection_time").to_list()
    )
    return documents


@router.get(
    "/{id}.pdf",
    dependencies=[Security(backend.get_current_user)],
)
async def download_document(
    target: RetrievedDocument = Depends(get_target),
):
    client = DocumentStorageClient()
    stream = client.read_document_stream(f"{target.checksum}.pdf")
    return StreamingResponse(stream, media_type="application/pdf")


@router.get(
    "/{id}",
    response_model=RetrievedDocument,
    dependencies=[Security(backend.get_current_user)],
)
async def read_document(
    target: RetrievedDocument = Depends(get_target),
):
    return target


@router.post("/{id}", response_model=RetrievedDocument)
async def update_document(
    updates: UpdateRetrievedDocument,
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(backend.get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)

    ace_turned_on = (
        updates.automated_content_extraction and not target.automated_content_extraction
    )
    ace_class_changed = (
        target.automated_content_extraction_class
        != updates.automated_content_extraction_class
    )
    if ace_turned_on or ace_class_changed:
        task = ContentExtractionTask(
            site_id=target.site_id,
            scrape_task_id=target.scrape_task_id,
            retrieved_document_id=target.id,
            queued_time=datetime.now(),
        )
        await task.save()

    return updated


@router.delete("/{id}")
async def delete_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(backend.get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(
        logger, current_user, target, UpdateRetrievedDocument(disabled=True)
    )
    return {"success": True}
