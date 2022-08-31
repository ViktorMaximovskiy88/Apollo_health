from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    delete_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.models.payer_backbone import PayerBackbone
from backend.common.models.user import User

router = APIRouter(
    prefix="/payer-backbone",
    tags=["PayerBackbone"],
)


async def get_target(id: PydanticObjectId) -> PayerBackbone:
    config = await PayerBackbone.get(id)
    if not config:
        raise HTTPException(
            detail=f"Payer Backbone {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return config


@router.get(
    "/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_payer_backbones(
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = PayerBackbone.find({})
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/{id}",
    response_model=PayerBackbone,
    dependencies=[Security(get_current_user)],
)
async def read_payer_backbone(
    target: PayerBackbone = Depends(get_target),
):
    return target


@router.put("/", response_model=PayerBackbone, status_code=status.HTTP_201_CREATED)
async def create_payerbackbone(
    pb: PayerBackbone,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await create_and_log(logger, current_user, pb)
    return pb


@router.delete("/{id}")
async def delete_payer_backbone(
    target: User = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await delete_and_log(logger, current_user, target)
    return {"success": True}


@router.post("/{id}", response_model=PayerBackbone)
async def update_translation_config(
    updates: PayerBackbone,
    target: PayerBackbone = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated
