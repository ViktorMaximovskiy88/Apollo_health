from datetime import datetime

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import StreamingResponse

from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.storage.client import DocumentStorageClient
from backend.common.events.send_event_client import SendEventClient
from backend.common.events.event_convert import EventConvert

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
    dependencies=[Security(get_current_user)],
)
async def get_documents(
    scrape_task_id: PydanticObjectId | None = None,
    site_id: PydanticObjectId | None = None,
    logical_document_id: PydanticObjectId | None = None,
    automated_content_extraction: bool | None = None,
):
    query = {}
    if scrape_task_id:
        scrape_task = await SiteScrapeTask.get(scrape_task_id)
        if not scrape_task:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, f"Scrape Task {scrape_task_id} does not exist")

        query["_id"] = {"$in": scrape_task.retrieved_document_ids}
    if site_id:
        query["site_id"] = site_id
    if logical_document_id:
        query["logical_document_id"] = logical_document_id
    if automated_content_extraction:
        query["automated_content_extraction"] = automated_content_extraction

    documents: list[RetrievedDocument] = (
        await RetrievedDocument.find_many(query).sort("-first_collected_date").to_list()
    )
    return documents


@router.get(
    "/",
    response_model=list[RetrievedDocument],
    dependencies=[Security(get_current_user)],
)
async def read_documents(
    documents: list[RetrievedDocument] = Depends(get_documents),
) -> list[RetrievedDocument]:
    return documents


@router.get("/{id}.pdf", dependencies=[Security(get_current_user)])
async def download_document(
    target: RetrievedDocument = Depends(get_target),
):
    client = DocumentStorageClient()
    stream = client.read_object_stream(f"{target.checksum}.pdf")
    return StreamingResponse(stream, media_type="application/pdf")


@router.get(
    "/{id}",
    response_model=RetrievedDocument,
    dependencies=[Security(get_current_user)],
)
async def read_document(
    target: RetrievedDocument = Depends(get_target),
):
    # TODO migration to fix this for reals...
    if target.file_extension is None:
        target.file_extension = "pdf"

    return target


@router.post("/{id}", response_model=RetrievedDocument)
async def update_document(
    updates: UpdateRetrievedDocument,
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
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
    # Sending Event Bridge Event.  Need to add condition when to send.
    document_json = EventConvert(document=updated).convert()
    send_evnt_client = SendEventClient()
    response = send_evnt_client.send_event("document-details", document_json)

    return updated


@router.delete("/{id}")
async def delete_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(
        logger, current_user, target, UpdateRetrievedDocument(disabled=True)
    )
    return {"success": True}
