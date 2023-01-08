import re
from urllib.parse import unquote

from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.core.settings import settings
from backend.app.utils.user import get_current_user
from backend.common.models.doc_document import DocDocument
from backend.common.models.lineage import LineageDoc
from backend.common.models.site import Site
from backend.common.models.tasks import LineageTask
from backend.common.models.user import User
from backend.common.tasks.task_queue import TaskQueue

task_queue = TaskQueue(
    queue_url=settings.task_worker_queue_url,
)

router = APIRouter(
    prefix="/devtools",
    tags=["Devtools"],
)


@router.post("/lineage/reprocess/{site_id}")
async def reprocess_lineage_for_site(
    site_id: PydanticObjectId,
    current_user: User = Security(get_current_user),
):
    task_payload = LineageTask(site_id=site_id, reprocess=True)
    task = await task_queue.enqueue(task_payload, current_user.id)
    return {"task": task}


def maybe_object_id(query: str):
    if len(query) != 24:
        return None

    try:
        return PydanticObjectId(query)
    except Exception:
        return None


@router.get(
    "/documents",
    dependencies=[Security(get_current_user)],
)
async def get_documents(
    search_query: str = "",
    site_id: PydanticObjectId | None = None,
    page: int = 0,
    limit: int = 50,
    sort: str = "-last_collected_date",
):
    max_limit = 50
    limit = max_limit if not limit or limit > max_limit else limit

    query = {}

    if site_id:
        query["locations.site_id"] = site_id

    if search_query:
        if search_query.startswith("http"):
            query["locations.url"] = unquote(search_query)
        elif id := maybe_object_id(search_query):
            query["_id.url"] = id
        else:
            query["$text"] = {"$search": search_query}

    if len(query.keys()):
        total_count = await DocDocument.find(query).count()
    else:
        total_count = await DocDocument.get_motor_collection().estimated_document_count()

    docs = await DocDocument.find(
        query, skip=page * limit, limit=limit, sort=sort, projection_model=LineageDoc
    ).to_list()

    return {"items": docs, "total_count": total_count}


@router.get(
    "/sites/search",
    dependencies=[Security(get_current_user)],
)
async def search_sites(search_query: str, limit: int = 20):
    # clamp
    max_limit = 50
    limit = max_limit if not limit or limit > max_limit else limit

    query = {"disabled": False}
    if search_query.startswith("http"):
        query["base_urls.url"] = unquote(search_query)
    elif id := maybe_object_id(search_query):
        query["_id"] = id

    if search_query:
        escaped = re.escape(search_query)
        query["name"] = {"$regex": f"^{escaped}", "$options": "i"}

    total_count = await Site.find(query).count()
    sites = await Site.find(
        query,
        limit=limit,
        sort="-last_run_time",
    ).to_list()

    return {"items": sites, "total_count": total_count}
