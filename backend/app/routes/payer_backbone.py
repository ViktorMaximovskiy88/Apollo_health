from datetime import datetime, timezone
from typing import Literal, Type

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
from backend.common.models.payer_backbone import PayerBackbone, PayerBackboneUnionDoc, payer_classes
from backend.common.models.user import User

router = APIRouter(
    prefix="/payer-backbone",
    tags=["PayerBackbone"],
)


async def get_target(id: PydanticObjectId):
    config = await PayerBackboneUnionDoc.find_one({"_id": id})
    if not config:
        raise HTTPException(
            detail=f"Payer Backbone {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return config


def payer_class(
    type: Literal["plan", "formulary", "mco", "parent", "ump", "bm"],
) -> Type[PayerBackbone]:
    return next((i for i in payer_classes if i.payer_key == type))


@router.get(
    "/{type}",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_payer_backbones(
    PayerClass: Type[PayerBackbone] = Depends(payer_class),
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    (class_filter,) = PayerClass._add_class_id_filter(())
    effective_date = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    date_str = effective_date.strftime("%Y-%m-%d")
    query = PayerBackboneUnionDoc.find(class_filter)
    filters.append(TableFilterInfo(name="start_date", operator="lte", type="date", value=date_str))
    filters.append(TableFilterInfo(name="end_date", operator="gt", type="date", value=date_str))
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/{type}/l/{id}",
    dependencies=[Security(get_current_user)],
)
async def read_payer_backbone_by_l_id(
    id: int,
    PayerClass: Type[PayerBackbone] = Depends(payer_class),
):
    payer = await PayerClass.find_one({"l_id": id})
    if not payer:
        raise HTTPException(
            detail=f"Payer Backbone LId {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return payer


@router.get(
    "/{type}/{id}",
    dependencies=[Security(get_current_user)],
)
async def read_payer_backbone(
    target=Depends(get_target),
):
    return target


@router.post("/{type}/{id}")
async def update_translation_config(
    updates: PayerBackbone,
    target: PayerBackbone = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{type}/{id}")
async def delete_payer_backbone(
    target: PayerBackbone = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await delete_and_log(logger, current_user, target)
    return {"success": True}


@router.put("/{type}", status_code=status.HTTP_201_CREATED)
async def create_payerbackbone(
    payer: PayerBackbone,
    PayerClass: Type[PayerBackbone] = Depends(payer_class),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    payer = PayerClass.parse_obj(payer.dict())
    await create_and_log(logger, current_user, payer)
    return payer
