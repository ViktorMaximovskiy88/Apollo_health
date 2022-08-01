import tempfile
from datetime import datetime

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Security, UploadFile
from fastapi.responses import StreamingResponse

from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLimitTags, UpdateRetrievedDocument
from backend.common.models.doc_document import DocDocument, calc_final_effective_date
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    get_logger,
    create_and_log,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.storage.client import DocumentStorageClient
from backend.common.events.send_event_client import SendEventClient
from backend.common.events.event_convert import EventConvert
from backend.common.storage.hash import hash_bytes
from backend.scrapeworker.common.text_handler import TextHandler
from backend.scrapeworker.file_parsers import parse_by_type
from backend.scrapeworker.common.models import Download, Request


router = APIRouter(
    prefix="/documents",
    tags=["Dcouments"],
)


async def get_target(id: PydanticObjectId) -> RetrievedDocument:
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
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                f"Scrape Task {scrape_task_id} does not exist",
            )

        query["_id"] = {"$in": scrape_task.retrieved_document_ids}
    if site_id:
        query["site_id"] = site_id
    if logical_document_id:
        query["logical_document_id"] = logical_document_id
    if automated_content_extraction:
        query["automated_content_extraction"] = automated_content_extraction

    documents: list[RetrievedDocumentLimitTags] = (
        await RetrievedDocument
          .find_many(query)
          .sort("-first_collected_date")
          .project(RetrievedDocumentLimitTags)
          .to_list()
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


@router.get("/viewer/{id}", dependencies=[Security(get_current_user)])
async def viewer_document_link(
    target: RetrievedDocument = Depends(get_target),
):
    client = DocumentStorageClient()
    url = client.get_signed_url(f"{target.checksum}.{target.file_extension}")
    return {"url": url}


@router.get(
    "/{id}",
    response_model=RetrievedDocument,
    dependencies=[Security(get_current_user)],
)
async def read_document(
    target: RetrievedDocument = Depends(get_target),
):
    return target


@router.post("/upload")
async def upload_document(
    file: UploadFile,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
): 
    text_handler = TextHandler()
    
    content = await file.read();
    checksum = hash_bytes(content);
    file_extension = file.content_type.split('/')[1]
    dest_path = f"{checksum}.{file_extension}"
    
    document = await RetrievedDocument.find_one(
        RetrievedDocument.checksum == checksum
        or checksum in RetrievedDocument.file_checksum_aliases
    )
    
    temp_path = ""
    with tempfile.NamedTemporaryFile(delete=True, suffix="." + file_extension) as tmp:
        tmp.write(content)
        temp_path = tmp.name

    download = Download(request=Request(url=temp_path), file_extension=file_extension)
    parsed_content = await parse_by_type(temp_path,download,[])

    text_checksum = await text_handler.save_text(parsed_content["text"])
    text_checksum_document = await RetrievedDocument.find_one(
        RetrievedDocument.text_checksum == text_checksum
    )

    # use first hash to see if their is a retrieved document
    if document or text_checksum_document:
        return {
            "error":f"This document already exists"
        }
    else:
        doc_client = DocumentStorageClient()
        if not doc_client.object_exists(dest_path):
            print('Uploading file...')
            doc_client.write_object(dest_path, temp_path, file.content_type)

        return {
            "success": True,
            "data": {
                dest_path:dest_path,
                checksum:checksum,
                text_checksum:text_checksum,
                parsed_content:parsed_content,
                content_type: file.content_type,
                file_extension: file_extension,
                name:file.name
            }
        }


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



@router.put("/", response_model=RetrievedDocument, status_code=status.HTTP_201_CREATED)
async def add_document(
    document: RetrievedDocument,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    now = datetime.now()
    document_file = document.document_file;
    parsed_content = document_file.parsed_content;
    new_document = RetrievedDocument(
        base_url=document.base_url,
        checksum=document_file.checksum,
        text_checksum=document_file.text_checksum,
        # context_metadata=download.metadata.dict(),
        doc_type_confidence=parsed_content["confidence"],
        document_type=parsed_content["document_type"],
        effective_date=document.effective_date,
        end_date=document.end_date,
        last_updated_date=document.last_updated_date,
        last_reviewed_date=document.last_reviewed_date,
        next_review_date=document.next_review_date,
        next_update_date=document.next_update_date,
        published_date=document.published_date,
        file_extension=document_file.file_extension,
        content_type=document_file.content_type,
        first_collected_date=now,
        identified_dates=parsed_content["identified_dates"],
        lang_code=document.lang_code,
        last_collected_date=now,
        metadata=parsed_content["metadata"],
        name=document_file.name,
        # scrape_task_id=self.scrape_task.id,
        site_id=document.site_id,
        url=document.url,
        therapy_tags=parsed_content["therapy_tags"],
        indication_tags=parsed_content["indication_tags"],
        file_checksum_aliases=set(document_file.checksum),
    )
    doc_document = DocDocument(
        site_id=document.site_id,
        retrieved_document_id=new_document.id,  # type: ignore
        name=document_file.name,
        checksum=document_file.checksum,
        text_checksum=document_file.text_checksum,
        document_type=parsed_content["document_type"],
        doc_type_confidence=parsed_content["confidence"],
        effective_date=document.effective_date,
        end_date=document.end_date,
        last_updated_date=document.last_updated_date,
        last_reviewed_date=document.last_reviewed_date,
        next_review_date=document.next_review_date,
        next_update_date=document.next_update_date,
        published_date=document.published_date,
        lang_code=document.lang_code,
        first_collected_date=now,
        last_collected_date=now,
        link_text=document.link_text,
        url=document.url,
        base_url=document.base_url,
        therapy_tags=parsed_content["therapy_tags"],
        indication_tags=parsed_content["indication_tags"],
        file_extension=document_file.file_extension,
        identified_dates=parsed_content["identified_dates"]
    )
    doc_document.final_effective_date = calc_final_effective_date(doc_document)
    await create_and_log(logger, current_user, new_document)
    
    await create_and_log(logger, current_user, doc_document)

































