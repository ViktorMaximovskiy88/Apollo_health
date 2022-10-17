import logging
from datetime import datetime, timezone
from typing import Any, TypeVar

from beanie import Document
from beanie.odm.operators.update.general import Set
from bson import json_util
from fastapi import BackgroundTasks
from jsonpatch import JsonPatch, JsonPointer
from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel

from backend.common.models.change_log import ChangeLog
from backend.common.models.user import User


class Logger:
    def __init__(self, background_tasks: BackgroundTasks | None = None) -> None:
        self.background_tasks = background_tasks

    async def log_change(self, user: User, target: Document, action: str, delta):
        collection = target.get_motor_collection().name
        log = ChangeLog(
            user_id=user.id,
            target_id=target.id,
            time=datetime.now(tz=timezone.utc),
            action=action,
            collection=collection,
            delta=delta,
        )
        await log.save()

    async def background_log_change(self, user: User, target: Document, action, delta=None):
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


def get_diff_patch(
    original: dict[str, Any],
    updated: dict[str, Any],
):
    patch = JsonPatch.from_diff(original, updated, dumps=json_util.dumps).patch
    for op in patch:
        if op["op"] == "remove" or op["op"] == "replace":
            pointer = JsonPointer(op["path"])
            try:
                op["prev"] = pointer.resolve(original)
            except Exception as ex:
                logging.debug(ex)
                pass
    return patch


async def delete_and_log(
    logger: Logger,
    current_user: User,
    target: Document,
    session: AsyncIOMotorClientSession | None = None,
):
    response = await target.delete(session=session)
    await logger.background_log_change(current_user, target, "DELETE")
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
    patch = get_diff_patch(original, updated)
    if patch:
        await logger.log_change(current_user, target, "UPDATE", patch)
    return updated
