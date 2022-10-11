import logging
import tempfile
from datetime import datetime, timezone
from typing import Any, List

import typer
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, status
from fastapi.responses import StreamingResponse

from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.core.enums import CollectionMethod
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import (
    NewManualDocument,
    RetrievedDocument,
    RetrievedDocumentLimitTags,
    RetrievedDocumentLocation,
    UpdateRetrievedDocument,
)
from backend.common.models.document_mixins import get_site_location
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import (
    ManualWorkItem,
    SiteScrapeTask,
    TaskStatus,
    WorkItemOption,
)
from backend.common.models.user import User
from backend.common.services.collection import CollectionResponse
from backend.common.services.document import create_doc_document_service
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_bytes
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.models import DownloadContext, Request
from backend.scrapeworker.file_parsers import parse_by_type

router: APIRouter = APIRouter(
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
        scrape_task: SiteScrapeTask | None = await SiteScrapeTask.get(scrape_task_id)
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
) -> StreamingResponse:
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
) -> RetrievedDocument:
    return target


@router.post("/upload/{from_site_id}", dependencies=[Security(get_current_user)])
async def upload_document(file: UploadFile, from_site_id: PydanticObjectId) -> dict[str, Any]:
    text_handler: TextHandler = TextHandler()
    content: bytes | str = await file.read()
    if isinstance(content, str):
        raise Exception("Invalid File Type")
    checksum: str = hash_bytes(content)
    content_type: str = file.content_type
    name: str = file.filename
    file_extension: str = name.split(".")[-1]
    dest_path: str = f"{checksum}.{file_extension}"
    response = {"success": True, "data": {}}

    checksum_document: RetrievedDocument | None = await RetrievedDocument.find_one(
        RetrievedDocument.checksum == checksum,
    )
    with tempfile.NamedTemporaryFile(delete=True, suffix="." + file_extension) as tmp:
        tmp.write(content)
        temp_path: str = tmp.name

        download: DownloadContext = DownloadContext(
            request=Request(url=temp_path), file_extension=file_extension
        )
        parsed_content: dict[str, Any] | None = await parse_by_type(temp_path, download)
        if not parsed_content:
            raise Exception("Count not extract file contents")

        text_checksum: str = await text_handler.save_text(parsed_content["text"])
        text_checksum_document: RetrievedDocument | None = await RetrievedDocument.find_one(
            RetrievedDocument.text_checksum == text_checksum
        )
        response["data"] = {
            "checksum": checksum,
            "text_checksum": text_checksum,
            "content_type": content_type,
            "file_extension": file_extension,
            "metadata": parsed_content["metadata"],
            "doc_type_confidence": str(parsed_content["confidence"]),
            "therapy_tags": parsed_content["therapy_tags"],
            "indication_tags": parsed_content["indication_tags"],
            "identified_dates": parsed_content["identified_dates"],
            "base_url": "",
            "url": "",
            "link_text": "",
        }

        # If uploaded doc exists, get location of existing doc and render to user.
        if checksum_document:
            checksum_location: RetrievedDocumentLocation = checksum_document.get_site_location(
                from_site_id
            )
            if checksum_location:
                response["data"]["base_url"] = checksum_location.base_url
                response["data"]["url"] = checksum_location.url
                response["data"]["link_text"] = checksum_location.link_text
        elif text_checksum_document:
            text_checksum_location: RetrievedDocumentLocation = (
                text_checksum_document.get_site_location(from_site_id)
            )
            if text_checksum_location:
                response["data"]["base_url"] = text_checksum_location.base_url
                response["data"]["url"] = text_checksum_location.url
                response["data"]["link_text"] = text_checksum_location.link_text
        else:
            doc_client: DocumentStorageClient = DocumentStorageClient()
            if not doc_client.object_exists(dest_path):
                logging.info("Uploading file...")
                doc_client.write_object(dest_path, temp_path, file.content_type)
        return response


@router.post("/{id}", response_model=RetrievedDocument)
async def update_document(
    updates: UpdateRetrievedDocument,
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UpdateRetrievedDocument(disabled=True))
    return {"success": True}


# One time use case for the PUT request below in order to pass in internal_document
@router.put(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CollectionResponse,
)
async def add_document(
    document: NewManualDocument,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
) -> CollectionResponse:
    now: datetime = datetime.now(tz=timezone.utc)
    link_text = document.metadata.get("link_text", None)

    # Check if trying to upload a doc which already exists for this site.
    existing_docs: List[RetrievedDocument] = await RetrievedDocument.find(
        {"locations.site_id": document.site_id}
    ).to_list()
    for existing_doc in existing_docs:
        existing_doc_location: RetrievedDocumentLocation = get_site_location(
            existing_doc, site_id=document.site_id
        )
        if (
            existing_doc_location.base_url == document.base_url
            and existing_doc_location.url == document.url
            and existing_doc_location.link_text == document.link_text
        ):
            raise HTTPException(status.HTTP_409_CONFLICT, "Doc already exists for that location")

    # Add uploaded document to retr_doc.
    new_document: RetrievedDocument = RetrievedDocument(
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
        first_collected_date=now,
        last_collected_date=now,
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
    # Is uploading new version from work_item action.
    if document.replacing_old_version_id:
        new_document.is_current_version = True

    # Create task and doc_doc with same details as retr_doc (uploaded).
    created_retr_doc: RetrievedDocument = await create_and_log(logger, current_user, new_document)
    created_doc_doc: DocDocument = await create_doc_document_service(new_document, current_user)

    # TODO: This works for new version, but what about add new doc to task?
    # Update old_doc work_item in work_list with new_doc and set prev_doc to old_doc.
    site: Site | None = await Site.find_one({"_id": document.site_id})
    if document.replacing_old_version_id:
        # TODO: Pass current_queue task from frontend instead of fetching.
        current_queued_task: SiteScrapeTask = await SiteScrapeTask.find_one(
            {
                "initiator_id": current_user.id,
                "status": f"{TaskStatus.IN_PROGRESS}",
                "collection_method": f"{CollectionMethod.Manual}",
            }
        )
        doc_index: int = next(
            i
            for i, wi in enumerate(current_queued_task.work_list)
            if f"{wi.document_id}" == document.replacing_old_version_id
        )

        if not doc_index:
            msg = "Error uploading new version. Not able to find old doc in work list"
            typer.secho(msg, fg=typer.colors.RED)
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg,
            )
        work_item = current_queued_task.work_list[doc_index]
        work_item.retrieved_document_id = new_document.id
        work_item.prev_doc = document.replacing_old_version_id
        work_item.selected = WorkItemOption.NEW_VERSION
        current_queued_task.work_list[doc_index] = work_item
        await current_queued_task.save()
        # TODO: Log update
        # task_updates["work_list"][doc_index]["_id"] = new_document.id
        # task_updates["work_list"][doc_index]["is_new"] = True
        # task_updates["work_list"][doc_index]["prev_doc"] = new_document.replacing_old_version_id
        # task_updates["work_list"][doc_index]["selected"] = WorkItemOption.NEW_VERSION
        # await update_and_log_diff(logger, current_user, current_queued_task, task_updates)
    # Create new task and work item for new document.
    else:
        scrape_task: SiteScrapeTask = SiteScrapeTask(
            initiator_id=current_user.id,
            site_id=document.site_id,
            retrieved_document_ids=[new_document.id],
            status=TaskStatus.FINISHED,
            queued_time=now,
            start_time=now,
            end_time=now,
            documents_found=1,
            collection_method=site.collection_method,
        )
        if created_doc_doc:
            scrape_task.work_list.append(
                ManualWorkItem(
                    document_id=f"{created_doc_doc.id}",
                    retrieved_document_id=f"{created_retr_doc.id}",
                )
            )
        await scrape_task.save()

    return CollectionResponse(success=True)
