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


@router.get(
    "/documents",
    dependencies=[Security(get_current_user)],
    response_model=list[
        LineageDoc,
    ],
)
async def get_documents(
    site_id: PydanticObjectId | None = None,
    page: int = 0,
    limit: int = 50,
    sort: str = "-last_collected_date",
):
    max_limit = 50
    limit = max_limit if not limit or limit > max_limit else limit
    query = {"locations.site_id": site_id} if site_id else {}

    docs = await DocDocument.find(
        query, skip=page * limit, limit=limit, sort=sort, projection_model=LineageDoc
    ).to_list()

    return docs


@router.get(
    "/sites/search",
    dependencies=[Security(get_current_user)],
    response_model=list[Site],
)
async def search_sites(search_query: str, limit: int = 20):
    # clamp
    max_limit = 50
    limit = max_limit if not limit or limit > max_limit else limit

    query = None
    if search_query.startswith("http"):
        query = {"base_urls.url": unquote(search_query)}
    elif len(search_query) == 24:
        try:
            query = {"_id": PydanticObjectId(search_query)}
        except Exception:
            pass

    if not search_query:
        query = {}

    if not query:
        escaped = search_query.replace("|", "\\|")
        query = {"name": {"$regex": f"^{escaped}", "$options": "i"}}

    sites = await Site.find(
        {"disabled": False, **query},
        limit=limit,
        sort="-last_run_time",
    ).to_list()

    return sites
