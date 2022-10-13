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
from backend.common.models.payer_family import NewPayerFamily, PayerFamily, UpdatePayerFamily
from backend.common.models.user import User

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

    query = PayerFamily.find_all()
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/search",
    dependencies=[Security(get_current_user)],
    response_model=PayerFamily,
)
async def read_payer_family_by_name(
    name: str,
):
    payer_family = await PayerFamily.find_one({"name": name})
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


@router.put("/", response_model=PayerFamily, status_code=status.HTTP_201_CREATED)
async def create_payer_family(
    payer_family: NewPayerFamily,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_payer_family = PayerFamily(
        name=payer_family.name,
        document_type=payer_family.document_type,
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
    return {"success": True}