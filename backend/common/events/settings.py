from pydantic import BaseSettings

from backend.common.core.config import config


class Settings(BaseSettings):
    event_bus_name: str = config["EVENT_BUS_ARN"]
    event_source: str = config["EVENT_SOURCE"]
    disable_sending_events: bool = False

    pass


settings = Settings()
