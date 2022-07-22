from typing import Any, TypeVar
from jsonpatch import JsonPatch, JsonPointer
from bson import json_util
from datetime import datetime
from beanie import Document
from fastapi import BackgroundTasks
from pydantic import BaseModel
from beanie.odm.operators.update.general import Set
from backend.common.models.change_log import ChangeLog
from backend.common.models.user import User
from motor.motor_asyncio import AsyncIOMotorClientSession


class Logger:
    def __init__(self, background_tasks: BackgroundTasks | None = None) -> None:
        self.background_tasks = background_tasks

    async def log_change(self, user: User, target: Document, action: str, delta):
        collection = target.get_motor_collection().name
        log = ChangeLog(
            user_id=user.id,
            target_id=target.id,
            time=datetime.now(),
            action=action,
            collection=collection,
            delta=delta,
        )
        await log.save()

    async def background_log_change(
        self, user: User, target: Document, action, delta=None
    ):
        if self.background_tasks:
            self.background_tasks.add_task(self.log_change, user, target, action, delta)
        else:
            await self.log_change(user, target, action, delta)


async def get_logger(background_tasks: BackgroundTasks):
    return Logger(background_tasks)

T = TypeVar("T", bound=Document)

async def create_and_log(
    logger: Logger,
    current_user: User,
    target: T,
    session: AsyncIOMotorClientSession | None = None,
) -> T:
    response = await target.save(session=session)
    await logger.background_log_change(current_user, target, "CREATE")
    return response


async def update_and_log_diff(
    logger: Logger,
    current_user: User,
    target: Document,
    updates: BaseModel | dict[str, Any],
    session: AsyncIOMotorClientSession | None = None,
):
    original = target.dict()
    if isinstance(updates, BaseModel):
        updates = updates.dict(exclude_unset=True)

    await target.update(Set(updates), session=session)
    updated = target.dict()
    patch = JsonPatch.from_diff(original, updated, dumps=json_util.dumps).patch
    for op in patch:
        if op["op"] == "remove" or op["op"] == "replace":
            pointer = JsonPointer(op["path"])
            try:
                op["prev"] = pointer.resolve(original)
            except:
                pass
    await logger.background_log_change(current_user, target, "UPDATE", patch)
    return updated
