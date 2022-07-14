from pydantic import BaseSettings
from backend.common.core.config import config


class Settings(BaseSettings):
    document_path: str = config["S3_DOCUMENT_PATH"]
    model_path: str = config["S3_MODEL_PATH"]
    endpoint_url: str = config["S3_ENDPOINT_URL"]
    document_bucket: str = config["S3_DOCUMENT_BUCKET"]
    pass


settings = Settings()
