from pydantic import BaseSettings
from backend.common.core.config import config


class Settings(BaseSettings):
    secret_key: str = config["SECRET_KEY"]
    access_token_expire_minutes: int = config["ACCESS_TOKEN_EXPIRE_MINUTES"]


settings = Settings()
