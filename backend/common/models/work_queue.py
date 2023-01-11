from typing import Any

from backend.common.models.base_document import BaseDocument, BaseModel


class SubmitAction(BaseModel):
    label: str
    submit_action: Any
    primary: bool = False
    reassignable: bool = False
    require_comment: bool = False
    dest_queue: str | None = None


class SubmitActionUpdate(BaseModel):
    label: str | None = None
    submit_action: Any | None = None
    primary: bool | None = None
    reassignable: bool | None = None
    require_comment: bool | None = None
    dest_queue: str | None = None


class WorkQueue(BaseDocument):
    name: str
    description: str | None = None
    collection_name: str
    update_model_name: str
    grace_period: int = 30
    frontend_component: str
    document_query: dict[Any, Any]
    user_query: dict[Any, Any]
    sort_query: list[str] = []
    submit_actions: list[SubmitAction]


class WorkQueueUpdate(BaseDocument):
    name: str | None = None
    description: str | None = None
    document_query: Any | None = None
    user_query: Any | None = None
    submit_actions: list[SubmitActionUpdate] | None = None
    collection_name: str | None = None
    grace_period: int | None = None
    frontend_component: str | None = None
