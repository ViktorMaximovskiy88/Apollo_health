from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Security
from backend.app.utils.security import get_password_hash
from backend.common.models.user import NewUser, User, UserPublic, UserUpdate
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)

from backend.app.utils.user import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


async def get_target(id: PydanticObjectId):
    user = await User.get(id)
    if not user:
        raise HTTPException(
            detail=f"User {id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return user


@router.get("/whoami", response_model=UserPublic)
async def read_current_user(
    current_user: User = Security(get_current_user),
) -> User:
    return current_user


@router.get(
    "/",
    response_model=list[UserPublic],
    dependencies=[Security(get_current_user)],
)
async def read_users():
    users: list[User] = await User.find_many({}).to_list()
    return users


@router.get(
    "/{id}",
    response_model=UserPublic,
    dependencies=[Security(get_current_user)],
)
async def read_user(
    target: User = Depends(get_target),
):
    return target


@router.put("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: NewUser,
    current_user: User = Security(get_current_admin_user),
    logger: Logger = Depends(get_logger),
):
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin or False,
        roles=user.roles or [],
        hashed_password=get_password_hash(user.password),
    )
    await create_and_log(logger, current_user, new_user)
    return new_user


@router.post("/{id}", response_model=UserPublic)
async def update_user(
    updates: UserUpdate,
    target: User = Depends(get_target),
    current_user: User = Security(get_current_admin_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_user(
    target: User = Depends(get_target),
    current_user: User = Security(get_current_admin_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, UserUpdate(disabled=True))
    return {"success": True}
