from datetime import datetime
from typing import Any

from pydantic import BaseModel
from backend.common.models.base_document import BaseDocument

class SubmitAction(BaseModel):
    label: str
    submit_action: Any
    primary: bool = False

class SubmitActionUpdate(BaseModel):
    label: str | None = None
    submit_action: Any | None = None
    primary: bool | None = None

class WorkQueue(BaseDocument):
    name: str
    description: str | None = None
    document_query: dict[Any, Any]
    user_query: dict[Any, Any]
    submit_actions: list[SubmitAction]
    disabled: bool = False

class WorkQueueUpdate(BaseDocument):
    name: str | None = None
    description: str | None = None
    document_query: Any | None = None
    user_query: Any | None = None
    submit_actions: list[SubmitActionUpdate] | None = None
    disabled: bool | None = None
