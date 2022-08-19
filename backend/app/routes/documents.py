import tempfile
from datetime import datetime, timezone

from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, status
from fastapi.responses import StreamingResponse

from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import DocDocument, calc_final_effective_date
from backend.common.models.document import (
    RetrievedDocument,
    RetrievedDocumentLimitTags,
    UpdateRetrievedDocument,
)
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_bytes
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.models import DownloadContext, Request
from backend.scrapeworker.document_tagging.indication_tagging import indication_tagger
from backend.scrapeworker.document_tagging.taggers import Taggers
from backend.scrapeworker.document_tagging.therapy_tagging import therapy_tagger
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


@router.post("/upload")
async def upload_document(
    file: UploadFile,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    text_handler = TextHandler()

    content = await file.read()
    checksum = hash_bytes(content)
    content_type = file.content_type
    name = file.filename
    file_extension = name.split(".")[-1]
    dest_path = f"{checksum}.{file_extension}"

    document = await RetrievedDocument.find_one(
        RetrievedDocument.checksum == checksum
        or checksum in RetrievedDocument.file_checksum_aliases
    )

    with tempfile.NamedTemporaryFile(delete=True, suffix="." + file_extension) as tmp:
        tmp.write(content)
        temp_path = tmp.name

        download = DownloadContext(request=Request(url=temp_path), file_extension=file_extension)
        taggers = Taggers(indication=indication_tagger, therapy=therapy_tagger)
        parsed_content = await parse_by_type(temp_path, download, taggers)

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

    ace_turned_on = updates.automated_content_extraction and not target.automated_content_extraction
    ace_class_changed = (
        target.automated_content_extraction_class != updates.automated_content_extraction_class
    )

    if ace_turned_on or ace_class_changed:
        task = ContentExtractionTask(
            site_id=target.site_id,
            scrape_task_id=target.scrape_task_id,
            retrieved_document_id=target.id,
            queued_time=datetime.now(tz=timezone.utc),
        )
        await task.save()

    return updated


@router.delete("/{id}")
async def delete_document(
    target: RetrievedDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UpdateRetrievedDocument(disabled=True))
    return {"success": True}


@router.put("/", status_code=status.HTTP_201_CREATED)
async def add_document(
    document: RetrievedDocument,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    now = datetime.now(tz=timezone.utc)

    new_document = RetrievedDocument(
        base_url=document.base_url,
        uploader_id=current_user.id,
        name=document.name,
        scrape_task_id=document.scrape_task_id,
        text_checksum=document.text_checksum,
        doc_type_confidence=document.doc_type_confidence,
        document_type=document.document_type,
        effective_date=document.effective_date,
        context_metadata=document.metadata,
        end_date=document.end_date,
        last_updated_date=document.last_updated_date,
        last_reviewed_date=document.last_reviewed_date,
        next_review_date=document.next_review_date,
        next_update_date=document.next_update_date,
        published_date=document.published_date,
        file_extension=document.file_extension,
        content_type=document.content_type,
        first_collected_date=now,
        identified_dates=document.identified_dates,
        lang_code=document.lang_code,
        last_collected_date=now,
        metadata=document.metadata,
        site_id=document.site_id,
        url=document.url,
        therapy_tags=document.therapy_tags,
        indication_tags=document.indication_tags,
        file_checksum_aliases=[document.checksum],
        checksum=document.checksum,
    )
    await create_and_log(logger, current_user, new_document)

    doc_document = DocDocument(
        site_id=document.site_id,
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
        first_collected_date=now,
        last_collected_date=now,
        url=document.url,
        base_url=document.base_url,
        therapy_tags=document.therapy_tags,
        indication_tags=document.indication_tags,
        file_extension=document.file_extension,
        identified_dates=document.identified_dates,
    )

    if "link_text" in document.metadata:
        doc_document.link_text = document.metadata["link_text"]

    doc_document.final_effective_date = calc_final_effective_date(doc_document)
    await create_and_log(logger, current_user, doc_document)

    scrape_task = await SiteScrapeTask.get(document.scrape_task_id)

    if document.id:
        # get retrieved_document from Doc Document
        doc_document = await DocDocument.find_one({"_id": document.id})
        if doc_document:
            index = scrape_task.retrieved_document_ids.index(doc_document.retrieved_document_id)
            if index >= 0:
                new_retrieved_documents = scrape_task.retrieved_document_ids
                new_retrieved_documents[index] = new_document.id
                await scrape_task.update(
                    Set({SiteScrapeTask.retrieved_document_ids: new_retrieved_documents})
                )

    else:
        await scrape_task.update(
            {"$inc": {"documents_found": 1}, "$push": {"retrieved_document_ids": new_document.id}}
        )

    return {"success": True}
