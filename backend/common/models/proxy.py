from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument

class ProxyCredentials(BaseModel):
    username_env_var: str
    password_env_var: str

class Proxy(BaseDocument):
    name: str
    endpoints: list[str]
    credentials: ProxyCredentials | None = None