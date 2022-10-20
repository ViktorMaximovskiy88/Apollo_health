from datetime import datetime, timezone

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
from backend.common.models.comment import Comment, NewComment, UpdateComment
from backend.common.models.user import User

router = APIRouter(prefix="/comments", tags=["Comment"])


async def get_target(id: PydanticObjectId) -> Comment:
    comment = await Comment.get(id)
    if not comment:
        raise HTTPException(detail=f"Comment {id} Not Found", status_code=status.HTTP_404_NOT_FOUND)
    return comment


@router.get("/", dependencies=[Security(get_current_user)], response_model=TableQueryResponse)
async def read_comments(
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = Comment.find_all()
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/{id}",
    response_model=Comment,
    dependencies=[Security(get_current_user)],
)
async def read_comment(
    target: Comment = Depends(get_target),
):
    return target


@router.put("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: NewComment,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    now = datetime.now(tz=timezone.utc)
    new_comment = Comment(
        time=now,
        target_id=comment.target_id,
        user_id=current_user.id,  # type: ignore
        text=comment.text,
    )
    await create_and_log(logger, current_user, new_comment)
    return new_comment


@router.post("/{id}", response_model=Comment)
async def update_comment(
    updates: UpdateComment,
    target: Comment = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_comment(
    target: Comment = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await delete_and_log(logger, current_user, target)
    return {"success": True}
