from pydantic import BaseSettings
from backend.common.core.config import config


class Settings(BaseSettings):
    event_bus_name: str = config["EVENT_BUS_ARN"]
    event_source: str  = config["EVENT_SOURCE"]
    
    pass


settings = Settings()
