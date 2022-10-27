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
    RetrievedDocument,
    RetrievedDocumentLimitTags,
    RetrievedDocumentLocation,
    UpdateRetrievedDocument,
    UploadedDocument,
)
from backend.common.models.shared import DocDocumentLocation
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import (
    ManualWorkItem,
    SiteScrapeTask,
    TaskStatus,
    WorkItemOption,
)
from backend.common.models.user import User
from backend.common.services.collection import CollectionResponse, find_work_item_index
from backend.common.services.document import create_doc_document_service
from backend.common.services.site import site_last_started_task
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_bytes
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.models import DownloadContext, Request
from backend.scrapeworker.file_parsers import parse_by_type


def copy_location_to(location: RetrievedDocumentLocation, data: dict) -> dict:
    # TODO: Copy doc info like effective date
    data["base_url"] = location.base_url
    data["url"] = location.url
    data["link_text"] = location.link_text
    data["closest_heading"] = location.closest_heading
    data["siblings_text"] = location.siblings_text
    data["url_therapy_tags"] = location.url_therapy_tags
    data["url_indication_tags"] = location.url_indication_tags
    data["link_therapy_tags"] = location.link_therapy_tags
    data["link_indication_tags"] = location.link_indication_tags
    data["old_location_site_id"] = location.site_id
    data["first_collected_date"] = location.first_collected_date
    data["last_collected_date"] = location.last_collected_date
    return data


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
) -> List[RetrievedDocumentLimitTags]:
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


# User can upload the same document based on checksum from 2 different Sites in
# both ‘Create Document’ and ‘Add new version’ scenarious.  All validation logic
# should take place on upload.  If system finds that this doc already exists
# but on different site, some fields like Effective Dates have to be defaulted
# from already existing doc.  ‘save’ logic has to be adjusted to create
# new location element in both Retrieved Doc and Doc Doc ‘location’ array
# instead of creating new docs in scenario when doc exists in different location
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

    checksum_documents: List[RetrievedDocument] = await RetrievedDocument.find(
        RetrievedDocument.checksum == checksum,
    ).to_list()
    for doc in checksum_documents:
        if not doc.locations:
            continue
        # Doc with checksum and location exists on THIS site.
        checksum_same_site: RetrievedDocumentLocation = doc.get_site_location(from_site_id)
        if checksum_same_site:
            return {"error": "The document already exists for this site!"}
        # Doc with checksum and location exists on OTHER site.
        checksum_location: RetrievedDocumentLocation = doc.locations[-1]
        if checksum_location:
            response["data"] = copy_location_to(checksum_location, response["data"])
            response["data"]["old_location_doc_id"] = doc.id
            break

    with tempfile.NamedTemporaryFile(delete=True, suffix="." + file_extension) as tmp:
        tmp.write(content)
        temp_path = tmp.name
        download: DownloadContext = DownloadContext(
            request=Request(url=temp_path), file_extension=file_extension
        )
        parsed_content: dict[str, Any] | None = await parse_by_type(temp_path, download)
        if not parsed_content:
            raise Exception("Count not extract file contents")

        text_checksum: str = await text_handler.save_text(parsed_content["text"])
        text_checksum_documents: List[RetrievedDocument] = await RetrievedDocument.find(
            RetrievedDocument.text_checksum == checksum,
        ).to_list()
        for doc in text_checksum_documents:
            if not doc.locations:
                continue
            # Doc with text_checksum and location exists on THIS site.
            text_checksum_same_site: RetrievedDocumentLocation = doc.get_site_location(from_site_id)
            if text_checksum_same_site:
                return {"error": "The document already exists for this site!"}
            # Doc with checksum and location exists on OTHER site.
            text_checksum_location: RetrievedDocumentLocation = doc.locations[-1]
            if text_checksum_location:
                response["data"] = copy_location_to(text_checksum_location, response["data"])
                response["data"]["old_location_doc_id"] = doc.id
                break

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
        } | response["data"]

        if not checksum_documents and not text_checksum_documents:
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
    response_model=List[DocDocument] | CollectionResponse,
)
async def add_document(
    uploaded_doc: UploadedDocument,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
) -> RetrievedDocument | CollectionResponse:
    site: Site | None = await Site.find_one({"_id": uploaded_doc.site_id})
    if not site:
        raise HTTPException(status.HTTP_409_CONFLICT, "Not able to upload document to site.")
    now: datetime = datetime.now(tz=timezone.utc)
    link_text = uploaded_doc.metadata.get("link_text", None)

    if uploaded_doc.old_location_doc_id:
        created_retr_doc: RetrievedDocument | None = await RetrievedDocument.find_one(
            {id: uploaded_doc.old_location_doc_id}
        )
        if not created_retr_doc:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Not able to upload document to site. Duplicate location error.",
            )
        retr_doc_loc: RetrievedDocumentLocation = created_retr_doc.get_site_location(
            uploaded_doc.old_location_site_id
        )
        # TODO: Double check that ALL fields are copied.
        # 1) Handle old location same as params.
        # 2) Handle old location different than params.
        new_doc_loc: RetrievedDocumentLocation = RetrievedDocumentLocation(
            url=retr_doc_loc.url,
            base_url=retr_doc_loc.base_url,
            first_collected_date=now,
            last_collected_date=now,
            site_id=uploaded_doc.site_id,
            link_text=link_text,
            context_metadata=uploaded_doc.metadata,
        )
        created_retr_doc.locations.append(f"{new_doc_loc}")
        created_doc_doc: DocDocument | None = await DocDocument.find_one(
            DocDocument.retrieved_document_id == created_retr_doc.id
        )
        new_doc_doc_loc: DocDocumentLocation = DocDocumentLocation(**new_doc_loc)
        created_doc_doc.locations.append(f"{new_doc_doc_loc}")
        await created_retr_doc.save()
        await created_doc_doc.save()
    else:
        # Create retr_doc and doc_doc from uploaded_doc.
        new_retr_document: RetrievedDocument = RetrievedDocument(
            checksum=uploaded_doc.checksum,
            content_type=uploaded_doc.content_type,
            doc_type_confidence=uploaded_doc.doc_type_confidence,
            document_type=uploaded_doc.document_type,
            effective_date=uploaded_doc.effective_date,
            end_date=uploaded_doc.end_date,
            file_extension=uploaded_doc.file_extension,
            identified_dates=uploaded_doc.identified_dates,
            indication_tags=uploaded_doc.indication_tags,
            lang_code=uploaded_doc.lang_code,
            last_reviewed_date=uploaded_doc.last_reviewed_date,
            last_updated_date=uploaded_doc.last_updated_date,
            metadata=uploaded_doc.metadata,
            name=uploaded_doc.name,
            next_review_date=uploaded_doc.next_review_date,
            next_update_date=uploaded_doc.next_update_date,
            published_date=uploaded_doc.published_date,
            text_checksum=uploaded_doc.text_checksum,
            therapy_tags=uploaded_doc.therapy_tags,
            uploader_id=current_user.id,
            first_collected_date=now,
            last_collected_date=now,
            locations=[
                RetrievedDocumentLocation(
                    url=uploaded_doc.url,
                    base_url=uploaded_doc.base_url,
                    first_collected_date=now,
                    last_collected_date=now,
                    site_id=uploaded_doc.site_id,
                    link_text=link_text,
                    context_metadata=uploaded_doc.metadata,
                )
            ],
        )

    # Set new_document current_version and lineage.
    # previous_doc_doc_id (a field on DocDocument) is a DocDocument id,
    # previous_doc_id (a field on RetrievedDocument) is a RetrievedDocument id.
    # lineage_id (a field on both DocDocument and RetrievedDocument) is a Lineage id,
    # from the Lineage table. a given pair of DocDocuments and RetrievedDocuments
    # will have the same lineage_id.
    new_retr_document.is_current_version = True
    if uploaded_doc.upload_new_version_for_id:
        original_doc_doc: DocDocument | None = await DocDocument.find_one(
            {"_id": PydanticObjectId(uploaded_doc.upload_new_version_for_id)}
        )
        original_doc_doc.is_current_version = False
        original_retr_doc: DocDocument | None = await RetrievedDocument.find_one(
            {"_id": PydanticObjectId(original_doc_doc.retrieved_document_id)}
        )
        original_retr_doc.is_current_version = False
        new_retr_document.previous_doc_id = original_retr_doc.id
        if original_retr_doc.lineage_id:
            new_retr_document.lineage_id = original_retr_doc.lineage_id
        elif original_doc_doc.lineage_id:
            new_retr_document.lineage_id = original_doc_doc.lineage_id
        else:
            err_msg: str = (
                f"New version error: not able to find lineage from original documents. "
                f"retr_doc_id: [{original_retr_doc.id}] doc_doc_id: [{original_doc_doc.id}] "
            )
            typer.secho(err_msg, fg=typer.colors.BRIGHT_RED)
        await original_retr_doc.save()
        await original_doc_doc.save()

    if not new_retr_document.lineage_id:
        new_retr_document.lineage_id = PydanticObjectId()
    if uploaded_doc.old_location_doc_id:
        created_retr_doc: RetrievedDocument = await create_and_log(
            logger, current_user, new_retr_document
        )
        created_doc_doc: DocDocument = await create_doc_document_service(
            new_retr_document, current_user
        )
    if uploaded_doc.upload_new_version_for_id and original_doc_doc.document_family_id:
        created_doc_doc.document_family_id = original_doc_doc.document_family_id
    # Need to update previous_doc_doc_id since new_retr_doc is retr_doc which does not have
    # a previous_doc_doc_id. New retr_document.previous_doc_id is set before create.
    if uploaded_doc.upload_new_version_for_id:
        created_doc_doc.previous_doc_doc_id = original_doc_doc.id
        await created_doc_doc.save()

    # Automatic: Add document to new task.
    if site.collection_method == CollectionMethod.Automated:
        new_scrape_task: SiteScrapeTask = SiteScrapeTask(
            initiator_id=current_user.id,
            site_id=uploaded_doc.site_id,
            retrieved_document_ids=[created_retr_doc.id],
            status=TaskStatus.FINISHED,
            queued_time=now,
            start_time=now,
            end_time=now,
            documents_found=1,
            collection_method=site.collection_method,
        )
        await new_scrape_task.save()
        return created_retr_doc

    # Manual: Process and update work items.
    current_task: SiteScrapeTask = await site_last_started_task(site.id)
    if not current_task:
        return created_retr_doc
    created_work_item: ManualWorkItem = ManualWorkItem(
        document_id=f"{created_doc_doc.id}",
        retrieved_document_id=f"{created_retr_doc.id}",
    )
    if uploaded_doc.upload_new_version_for_id:  # new version
        created_work_item.selected = WorkItemOption.NEW_VERSION
        created_work_item.is_new = False
    else:
        created_work_item.selected = WorkItemOption.NEW_DOCUMENT
    current_task.work_list.append(created_work_item)
    # Set work_item current_version and lineage.
    if uploaded_doc.upload_new_version_for_id:
        # Set old version's work_item as not current.
        original_item_index: int = find_work_item_index(
            original_retr_doc, current_task, raise_exception=True
        )
        original_item = current_task.work_list[original_item_index]
        original_item.is_current_version = False
        original_item.is_new = False
        original_item.selected = WorkItemOption.NOT_FOUND
        original_item.new_doc = created_retr_doc.id
        current_task.work_list[original_item_index] = original_item
        # Update new version's prev_doc to old version and set as current.
        created_item_index: int = find_work_item_index(
            created_retr_doc, current_task, raise_exception=True
        )
        created_item = current_task.work_list[created_item_index]
        created_item.prev_doc = original_retr_doc.id
        created_item.is_current_version = True
        created_item.is_new = False
        current_task.work_list[created_item_index] = created_item
    # Save updated work_list and add to task.retr_doc_ids for querying.
    current_task.retrieved_document_ids.append(f"{created_retr_doc.id}")
    await current_task.save()

    return created_retr_doc
