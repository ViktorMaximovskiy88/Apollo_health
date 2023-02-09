import asyncio
import logging
import re
from typing import Type

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.routes.payer_backbone import payer_class
from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.services.payer_backbone.payer_backbone_querier import (
    ControlledLivesResponse,
    PayerBackboneQuerier,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.doc_document import BulkUpdateResponse, DocDocument, UpdateDocDocument
from backend.common.models.payer_backbone import PayerBackbone
from backend.common.models.payer_family import NewPayerFamily, PayerFamily, UpdatePayerFamily
from backend.common.models.user import User
from backend.common.repositories.doc_document_repository import DocDocumentRepository

router = APIRouter(prefix="/payer-family", tags=["Payer Family"])


async def get_target(id: PydanticObjectId) -> PayerFamily:
    payer_family = await PayerFamily.get(id)
    if not payer_family:
        raise HTTPException(
            detail=f"Payer Family {id} Not FOUND", status_code=status.HTTP_404_NOT_FOUND
        )
    return payer_family


@router.get("/", dependencies=[Security(get_current_user)], response_model=TableQueryResponse)
async def read_payer_families(
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):

    query = PayerFamily.find({"disabled": False})
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/search",
    dependencies=[Security(get_current_user)],
    response_model=PayerFamily,
)
async def read_payer_family_by_name(
    name: str,
):
    new_name = re.escape(name)
    payer_family = await PayerFamily.find(
        {"name": {"$regex": f"^{new_name}$", "$options": "i"}, "disabled": False}
    ).first_or_none()

    return payer_family


@router.get(
    "/{id}",
    response_model=PayerFamily,
    dependencies=[Security(get_current_user)],
)
async def read_payer_family(
    target: PayerFamily = Depends(get_target),
):
    return target


@router.get("/{id}/convert", dependencies=[Security(get_current_user)], response_model=PayerFamily)
async def payer_family_payer_data(
    effective_date: str | None = None,
    PayerClass: Type[PayerBackbone] = Depends(payer_class),
    target: PayerFamily = Depends(get_target),
):
    pbbq = PayerBackboneQuerier(target, effective_date)

    result_ids = await pbbq.relevant_payer_ids_of_type(PayerClass)

    target.payer_type = PayerClass.payer_key
    target.payer_ids = [str(id) for id in result_ids]
    return target


@router.get(
    "/{id}/lives-by-controller",
    dependencies=[Security(get_current_user)],
    response_model=list[ControlledLivesResponse],
)
async def lives_by_controller(
    effective_date: str | None = None,
    target: PayerFamily = Depends(get_target),
):
    pbbq = PayerBackboneQuerier(target, effective_date)
    result = await pbbq.lives_by_controller()
    return result


@router.post(
    "/convert/{type}", dependencies=[Security(get_current_user)], response_model=PayerFamily
)
async def convert_document_family_payer_data(
    target: PayerFamily,
    effective_date: str | None = None,
    PayerClass: Type[PayerBackbone] = Depends(payer_class),
):
    pbbq = PayerBackboneQuerier(target, effective_date)

    result_ids = await pbbq.relevant_payer_ids_of_type(PayerClass)

    if not result_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Payer Family must match at least one plan",
        )

    target.payer_type = PayerClass.payer_key
    target.payer_ids = [str(id) for id in result_ids]
    return target


@router.put("/", response_model=PayerFamily, status_code=status.HTTP_201_CREATED)
async def create_payer_family(
    payer_family: NewPayerFamily,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_payer_family = PayerFamily(
        name=payer_family.name,
        payer_type=payer_family.payer_type,
        payer_ids=payer_family.payer_ids,
        channels=payer_family.channels,
        benefits=payer_family.benefits,
        plan_types=payer_family.plan_types,
        regions=payer_family.regions,
        disabled=False,
    )
    await create_and_log(logger, current_user, new_payer_family)
    return new_payer_family


@router.post("/{id}", response_model=PayerFamily)
async def update_payer_family(
    updates: UpdatePayerFamily,
    target: PayerFamily = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_payer_family(
    id: PydanticObjectId,
    target: PayerFamily = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UpdatePayerFamily(disabled=True))
    doc_documents_repo = DocDocumentRepository()

    docs = await DocDocument.find_many(
        {"locations.payer_family_id": id},
    ).to_list()

    counts, errors = {"suc": 0, "err": 0}, []

    async def gather_tasks(tasks):
        for res in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(res, Exception):
                errors.append(str(res))
                counts["err"] += 1
                logging.error(res, exc_info=True)
            else:
                counts["suc"] += 1

    tasks = []
    for doc in docs:
        for location in doc.locations:
            if location.payer_family_id == id:
                location.payer_family_id = None
        tasks.append(
            doc_documents_repo.execute(
                doc, UpdateDocDocument(locations=doc.locations), current_user
            )
        )
        if len(tasks) == 10:
            await gather_tasks(tasks)
            tasks = []

    await gather_tasks(tasks)

    return BulkUpdateResponse(count_success=counts["suc"], count_error=counts["err"], errors=errors)
