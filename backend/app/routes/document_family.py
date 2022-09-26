from typing import Type

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.routes.payer_backbone import payer_class
from backend.app.services.payer_backbone.payer_backbone_querier import PayerBackboneQuerier
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.document_family import (
    DocumentFamily,
    NewDocumentFamily,
    UpdateDocumentFamily,
)
from backend.common.models.payer_backbone import PayerBackbone
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


@router.get(
    "/",
    dependencies=[Security(get_current_user)],
    response_model=list[DocumentFamily],
)
async def read_document_families(
    site_id: PydanticObjectId | None = None,
    document_type: str | None = None,
):
    query = DocumentFamily.find({"disabled": False})

    if site_id:
        query = query.find({"site_id": site_id})

    if document_type:
        query = query.find({"document_type": document_type})

    return await query.to_list()


@router.get(
    "/search",
    dependencies=[Security(get_current_user)],
    response_model=DocumentFamily,
)
async def read_document_family_by_name(
    site_id: PydanticObjectId,
    name: str,
):
    document_families = await DocumentFamily.find_one({"name": name, "site_id": site_id})
    return document_families


@router.get(
    "/{id}",
    response_model=DocumentFamily,
    dependencies=[Security(get_current_user)],
)
async def read_document_family(
    target: DocumentFamily = Depends(get_target),
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
        payer_info=document_family.payer_info,
        disabled=False,
    )
    await create_and_log(logger, current_user, new_document_family)
    return new_document_family


@router.post(
    "/{id}/convert", dependencies=[Security(get_current_user)], response_model=DocumentFamily
)
async def document_family_payer_data(
    effective_date: str | None = None,
    PayerClass: Type[PayerBackbone] = Depends(payer_class),
    target: DocumentFamily = Depends(get_target),
):
    pbbq = PayerBackboneQuerier(target.payer_info, effective_date)
    result_ids = await pbbq.relevant_payer_ids_of_type(PayerClass)

    target.payer_info.payer_type = PayerClass.payer_key
    target.payer_info.payer_ids = [str(id) for id in result_ids]
    return target


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
