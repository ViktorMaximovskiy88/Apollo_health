from pydantic import BaseSettings
from backend.common.core.config import config


class Settings(BaseSettings):
    mongo_url: str = config["MONGO_URL"]
    mongo_db: str = config["MONGO_DB"]
    mongo_user: str = config.get("MONGO_USER", None)
    mongo_password: str = config.get("MONGO_PASSWORD", None)


settings = Settings()
