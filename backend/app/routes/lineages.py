from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.models.document import RetrievedDocument
from backend.common.models.lineage import Lineage, LineageDocumentEntry, LineageView

router = APIRouter(
    prefix="/lineages",
    tags=["Lineage"],
)


async def populate_docs(lineage: Lineage):
    doc_ids = [entry.doc_id for entry in lineage.entries]
    docs = await RetrievedDocument.find({"_id": {"$in": doc_ids}}).to_list()
    lineage_view = LineageView(id=lineage.id, current_version=lineage.current_version)
    lineage_view.entries = [LineageDocumentEntry(doc=doc) for doc in docs]
    return lineage_view


@router.get(
    "/document/{doc_id}",
    response_model=LineageView,
    dependencies=[Security(get_current_user)],
)
async def lineages_for_doc_id(doc_id: PydanticObjectId):
    lineage: Lineage = await Lineage.find_one({"entries.doc_id": doc_id})
    return await populate_docs(lineage)


@router.get(
    "/{lineage_id}",
    response_model=LineageView,
    dependencies=[Security(get_current_user)],
)
async def lineages_for_id(lineage_id: PydanticObjectId):
    lineage: Lineage = await Lineage.get(lineage_id)
    return await populate_docs(lineage)
