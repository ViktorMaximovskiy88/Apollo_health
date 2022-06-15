from playwright.async_api import ProxySettings
from pydantic import BaseSettings
from backend.common.core.config import config
from backend.common.models.proxy import Proxy
from backend.common.core.config import env_type
from random import choice

class Settings(BaseSettings):
    disable_proxies: bool = config.get('DISABLE_PROXIES', False)

settings = Settings()

class ProxyCredentailException(Exception):
    pass

def extract_proxy_creds_from_env(proxy: Proxy) -> ProxySettings | None:
    if proxy.credentials:
        username = config.get(proxy.credentials.username_env_var, None)
        password = config.get(proxy.credentials.password_env_var, None)
        if username and password:
            print(f"Using proxy {proxy.name} with credentials")
            return ProxySettings(
                server=choice(proxy.endpoints),
                username=username,
                password=password
            )
    else:
        print(f"Using proxy {proxy.name} no credentials")
        return ProxySettings(server=choice(proxy.endpoints))

def proxy_settings_internal(proxies: list[Proxy]) -> list[tuple[Proxy | None, ProxySettings | None]]:
    if not proxies:
        raise ProxyCredentailException(f"No proxies available for site")

    proxy_settings = []
    for proxy in proxies:
        if settings := extract_proxy_creds_from_env(proxy):
            proxy_settings.append((proxy, settings))

    if not proxy_settings:
        raise ProxyCredentailException(f"No credentials for valid proxies of site")

    return proxy_settings

def convert_proxies_to_proxy_settings(proxies: list[Proxy]) -> list[tuple[Proxy | None, ProxySettings | None]]:
    if settings.disable_proxies:
        return [(None, None)]

    try:
        return proxy_settings_internal(proxies)
    except ProxyCredentailException:
        if env_type == 'local':
            return [(None, None)]
        raise