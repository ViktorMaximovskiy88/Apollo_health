from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.doc_document import DocDocument
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


@router.get(
    "/",
    dependencies=[Security(get_current_user)],
    response_model=TableQueryResponse,
)
async def read_document_families(
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
    document_type: str | None = None,
):
    query = DocumentFamily.find({"disabled": False})

    if document_type:
        query = query.find({"document_type": document_type})

    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/search",
    dependencies=[Security(get_current_user)],
    response_model=DocumentFamily,
)
async def read_document_family_by_name(
    name: str,
    site_id: PydanticObjectId | None = None,
):
    if site_id:
        document_family = await DocumentFamily.find_one({"name": name, "site_id": site_id})
    document_family = await DocumentFamily.find_one({"name": name})
    return document_family


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
        relevance=document_family.relevance,
        field_groups=document_family.field_groups,
        legacy_relevance=document_family.legacy_relevance,
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
    await DocDocument.get_motor_collection().update_many(
        {"document_family_id": id}, {"$set": {"document_family_id": None}}
    )
    return {"success": True}
