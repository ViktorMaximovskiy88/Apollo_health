from pydantic import BaseSettings
from backend.common.core.config import config


class Settings(BaseSettings):
    mongo_url: str = config["MONGO_URL"]
    mongo_db: str = config["MONGO_DB"]
    mongo_user: str = config["MONGO_USER"]
    mongo_password: str = config["MONGO_PASSWORD"]


settings = Settings()
