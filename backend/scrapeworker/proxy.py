from playwright.async_api import ProxySettings
from pydantic import BaseSettings
from backend.common.core.config import config


class Settings(BaseSettings):
    server: str | None = config.get("PROXY_SERVER")
    username: str | None = config.get("PROXY_USERNAME")
    password: str | None = config.get("PROXY_PASSWORD")

settings = Settings()

def proxy_settings() -> ProxySettings | None:
    if settings.server:
        proxy_settings = ProxySettings(
            server= settings.server,
            username= settings.username,
            password= settings.password
        )
        return proxy_settings