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
from backend.common.models.base_document import BaseDocument
from backend.common.models.payer_backbone import (
    MCO,
    UMP,
    BenefitManager,
    DrugList,
    Formulary,
    PayerBackbone,
    PayerBackboneUnionDoc,
    PayerParent,
    Plan,
)
from backend.common.models.user import User

router = APIRouter(
    prefix="/payer-backbone",
    tags=["PayerBackbone"],
)


async def get_target(id: PydanticObjectId) -> PayerBackbone:
    config = await PayerBackboneUnionDoc.find_one({"_id": id})
    if not config:
        raise HTTPException(
            detail=f"Payer Backbone {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return config  # type: ignore


@router.get(
    "/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_payer_backbones(
    type: Literal["plan", "formulary", "mco", "parent", "ump", "bm"],
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = BaseDocument.find({})
    return await query_table(query, limit, skip, sorts, filters)


def creates(model: Type[BaseDocument]):
    @router.get(
        "/{id}",
        dependencies=[Security(get_current_user)],
    )
    async def read_payer_backbone(
        target=Depends(get_target),
    ):
        return target

    @router.post("/{id}")
    async def update_translation_config(
        updates: PayerBackbone,
        target: PayerBackbone = Depends(get_target),
        current_user: User = Security(get_current_user),
        logger: Logger = Depends(get_logger),
    ):
        updated = await update_and_log_diff(logger, current_user, target, updates)
        return updated

    @router.delete("/{id}")
    async def delete_payer_backbone(
        target: PayerBackbone = Depends(get_target),
        current_user: User = Security(get_current_user),
        logger: Logger = Depends(get_logger),
    ):
        await delete_and_log(logger, current_user, target)
        return {"success": True}

    @router.put(f"/{clazz.payer_key}", status_code=status.HTTP_201_CREATED)
    async def create_payerbackbone(
        pb: model,
        current_user: User = Security(get_current_user),
        logger: Logger = Depends(get_logger),
    ):
        await create_and_log(logger, current_user, pb)
        return pb


payer_types: list[Type[PayerBackbone]] = [
    UMP,
    MCO,
    Plan,
    DrugList,
    Formulary,
    PayerParent,
    BenefitManager,
]
for clazz in payer_types:
    creates(clazz)
