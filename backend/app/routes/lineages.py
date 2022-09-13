from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.models.lineage import Lineage

router = APIRouter(
    prefix="/lineages",
    tags=["Lineage"],
)


@router.get(
    "/{lineage_id}",
    response_model=list[Lineage],
    dependencies=[Security(get_current_user)],
)
async def lineages_for_id(lineage_id: PydanticObjectId):
    lineage: Lineage = await Lineage.get(lineage_id)
    return lineage
