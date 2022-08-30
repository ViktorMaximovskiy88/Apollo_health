import tempfile
from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, status
from fastapi.responses import StreamingResponse

from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.events.event_convert import EventConvert
from backend.common.events.send_event_client import SendEventClient
from backend.common.models.doc_document import DocDocument, DocDocumentLocation
from backend.common.models.document import (
    RetrievedDocument,
    RetrievedDocumentLimitTags,
    RetrievedDocumentLocation,
    SiteRetrievedDocument,
    UpdateRetrievedDocument,
)
from backend.common.models.site_scrape_task import SiteScrapeTask, TaskStatus
from backend.common.models.user import User
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_bytes
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.models import DownloadContext, Request
from backend.scrapeworker.file_parsers import parse_by_type

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
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
        query["locations.site_id"] = site_id

    documents: list[RetrievedDocumentLimitTags] = (
        await RetrievedDocument.find_many(query)
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
    s3_key = (
        f"{target.checksum}.{target.file_extension}.pdf"
        if target.file_extension == "html"
        else f"{target.checksum}.{target.file_extension}"
    )
    stream = client.read_object_stream(s3_key)
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


@router.post("/upload", dependencies=[Security(get_current_user)])
async def upload_document(
    file: UploadFile,
):
    text_handler = TextHandler()

    content = await file.read()
    if isinstance(content, str):
        raise Exception("Invalid File Type")

    checksum = hash_bytes(content)
    content_type = file.content_type
    name = file.filename
    file_extension = name.split(".")[-1]
    dest_path = f"{checksum}.{file_extension}"

    document = await RetrievedDocument.find_one(RetrievedDocument.checksum == checksum)

    with tempfile.NamedTemporaryFile(delete=True, suffix="." + file_extension) as tmp:
        tmp.write(content)
        temp_path = tmp.name

        download = DownloadContext(request=Request(url=temp_path), file_extension=file_extension)
        parsed_content = await parse_by_type(temp_path, download)
        if not parsed_content:
            raise Exception("Count not extract file contents")

        text_checksum = await text_handler.save_text(parsed_content["text"])
        text_checksum_document = await RetrievedDocument.find_one(
            RetrievedDocument.text_checksum == text_checksum
        )

        # use first hash to see if their is a retrieved document
        if document or text_checksum_document:
            return {"error": "The document already exists!"}
        else:
            doc_client = DocumentStorageClient()
            if not doc_client.object_exists(dest_path):
                print("Uploading file...")
                doc_client.write_object(dest_path, temp_path, file.content_type)

            return {
                "success": True,
                "data": {
                    "checksum": checksum,
                    "text_checksum": text_checksum,
                    "content_type": content_type,
                    "file_extension": file_extension,
                    "metadata": parsed_content["metadata"],
                    "doc_type_confidence": str(parsed_content["confidence"]),
                    "therapy_tags": parsed_content["therapy_tags"],
                    "indication_tags": parsed_content["indication_tags"],
                    "identified_dates": parsed_content["identified_dates"],
                },
            }


@router.post("/{id}", response_model=RetrievedDocument)
async def update_document(
    updates: UpdateRetrievedDocument,
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):

    updated = await update_and_log_diff(logger, current_user, target, updates)

    # Sending Event Bridge Event.  Need to add condition when to send.
    document_json = EventConvert(document=updated).convert()
    send_evnt_client = SendEventClient()
    response = send_evnt_client.send_event("document-details", document_json)  # noqa: F841

    return updated


@router.delete("/{id}")
async def delete_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UpdateRetrievedDocument(disabled=True))
    return {"success": True}


@router.put("/", status_code=status.HTTP_201_CREATED, response_model=SiteScrapeTask)
async def add_document(
    # verify we only want SiteRetrievedDocument
    document: SiteRetrievedDocument | RetrievedDocument,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    now = datetime.now(tz=timezone.utc)

    link_text = document.metadata["link_text"] if "link_text" in document.metadata else None

    new_document = RetrievedDocument(
        checksum=document.checksum,
        content_type=document.content_type,
        doc_type_confidence=document.doc_type_confidence,
        document_type=document.document_type,
        effective_date=document.effective_date,
        end_date=document.end_date,
        file_extension=document.file_extension,
        identified_dates=document.identified_dates,
        indication_tags=document.indication_tags,
        lang_code=document.lang_code,
        last_reviewed_date=document.last_reviewed_date,
        last_updated_date=document.last_updated_date,
        metadata=document.metadata,
        name=document.name,
        next_review_date=document.next_review_date,
        next_update_date=document.next_update_date,
        published_date=document.published_date,
        text_checksum=document.text_checksum,
        therapy_tags=document.therapy_tags,
        uploader_id=current_user.id,
        locations=[
            RetrievedDocumentLocation(
                url=document.url,
                base_url=document.base_url,
                first_collected_date=now,
                last_collected_date=now,
                site_id=document.site_id,
                link_text=link_text,
                context_metadata=document.metadata,
            )
        ],
    )

    await create_and_log(logger, current_user, new_document)

    doc_document = DocDocument(
        retrieved_document_id=new_document.id,  # type: ignore
        name=document.name,
        checksum=document.checksum,
        text_checksum=document.text_checksum,
        document_type=document.document_type,
        doc_type_confidence=document.doc_type_confidence,
        effective_date=document.effective_date,
        end_date=document.end_date,
        last_updated_date=document.last_updated_date,
        last_reviewed_date=document.last_reviewed_date,
        next_review_date=document.next_review_date,
        next_update_date=document.next_update_date,
        published_date=document.published_date,
        lang_code=document.lang_code,
        therapy_tags=document.therapy_tags,
        indication_tags=document.indication_tags,
        file_extension=document.file_extension,
        identified_dates=document.identified_dates,
        locations=[
            DocDocumentLocation(
                site_id=document.site_id,
                first_collected_date=now,
                last_collected_date=now,
                url=document.url,
                base_url=document.base_url,
                link_text=link_text,
            )
        ],
    )

    doc_document.set_final_effective_date()
    await create_and_log(logger, current_user, doc_document)

    scrape_task = SiteScrapeTask(
        site_id=document.site_id,
        retrieved_document_ids=[new_document.id],
        status=TaskStatus.FINISHED,
        queued_time=now,
        start_time=now,
        end_time=now,
        documents_found=1,
    )
    await scrape_task.save()

    return scrape_task
