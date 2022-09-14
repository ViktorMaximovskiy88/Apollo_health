from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.models.document import RetrievedDocument
from backend.common.models.lineage import Lineage

router = APIRouter(
    prefix="/lineages",
    tags=["Lineage"],
)


async def populate_docs(lineage: Lineage):
    doc_ids = [entry.doc_id for entry in lineage.entries]
    docs = await RetrievedDocument.find({"_id": {"$in": doc_ids}}).to_list()
    lineage.docs = docs
    return lineage


@router.get(
    "/document/{doc_id}",
    response_model=list[any],
    dependencies=[Security(get_current_user)],
)
async def lineages_for_doc_id(doc_id: PydanticObjectId):
    lineage: Lineage = await Lineage.find({"entries.doc_id": doc_id}).to_list()
    return await populate_docs(lineage)


@router.get(
    "/{lineage_id}",
    response_model=list[any],
    dependencies=[Security(get_current_user)],
)
async def lineages_for_id(lineage_id: PydanticObjectId):
    lineage: Lineage = await Lineage.get(lineage_id)
    return await populate_docs(lineage)
