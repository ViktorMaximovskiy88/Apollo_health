from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.document_family import (
    DocumentFamily,
    NewDocumentFamily,
    UpdateDocumentFamily,
)
from backend.common.models.user import User

router = APIRouter(
    prefix="/document-family",
    tags=["Document Family"],
)


async def get_target(id: PydanticObjectId) -> DocumentFamily:
    document_family = await DocumentFamily.get(id)
    if not document_family:
        raise HTTPException(
            detail=f"Document Family {id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return document_family


@router.get("/", response_model=list[DocumentFamily])
async def read_document_families(
    current_user: User = Security(get_current_user),
    site_id: str | None = None,
    document_type: str | None = None,
):
    query = DocumentFamily.find(
        {
            "disabled": False,
        }
    )
    if site_id:
        query = query.find({"site_id": PydanticObjectId(site_id)})
    if document_type:
        query = query.find({"document_type": document_type})

    return await query.to_list()


@router.get(
    "/search",
)
async def read_document_family_by_name(
    name: str,
    site_id: str,
    current_user: User = Security(get_current_user),
):
    if not site_id:
        raise HTTPException(
            detail=f"site_id was not given, instead recieved: {site_id}",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if not name:
        return None
    found = await DocumentFamily.find_one({"name": name, "site_id": PydanticObjectId(site_id)})
    return found


@router.get(
    "/{id}",
    response_model=DocumentFamily,
)
async def read_document_family(
    target: DocumentFamily = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    return target


@router.put("/", response_model=DocumentFamily, status_code=status.HTTP_201_CREATED)
async def create_document_family(
    document_family: NewDocumentFamily,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_document_family = DocumentFamily(
        name=document_family.name,
        document_type=document_family.document_type,
        description=document_family.description,
        site_id=document_family.site_id,
        relevance=document_family.relevance,
        disabled=False,
    )
    await create_and_log(logger, current_user, new_document_family)
    return new_document_family


@router.post("/{id}", response_model=DocumentFamily)
async def update_document_family(
    updates: UpdateDocumentFamily,
    target: DocumentFamily = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_document_family(
    id: PydanticObjectId,
    target: DocumentFamily = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UpdateDocumentFamily(disabled=True))
    return {"success": True}
