from playwright.async_api import ProxySettings
from pydantic import BaseSettings

from backend.common.core.config import config, env_type
from backend.common.models.proxy import Proxy


class Settings(BaseSettings):
    disable_proxies: bool = config.get("DISABLE_PROXIES", False)


settings = Settings()


class ProxyCredentailException(Exception):
    pass


def extract_proxy_creds_from_env(proxy: Proxy) -> list[ProxySettings | None]:
    proxy_settings_list = []
    if proxy.credentials:
        username = config.get(proxy.credentials.username_env_var, None)
        password = config.get(proxy.credentials.password_env_var, None)
        if username and password:
            for endpoint in proxy.endpoints:
                proxy_settings = ProxySettings(
                    server=endpoint, username=username, password=password
                )
                proxy_settings_list.append(proxy_settings)
    else:
        for endpoint in proxy.endpoints:
            proxy_settings_list.append(ProxySettings(server=endpoint))
    return proxy_settings_list


def proxy_settings_internal(
    proxies: list[Proxy],
) -> list[tuple[Proxy | None, ProxySettings | None]]:
    if not proxies:
        raise ProxyCredentailException("No proxies available for site")

    proxy_settings = []
    for proxy in proxies:
        if settings := extract_proxy_creds_from_env(proxy):
            for setting in settings:
                proxy_settings.append((proxy, setting))

    if not proxy_settings:
        raise ProxyCredentailException("No credentials for valid proxies of site")

    return proxy_settings


def convert_proxies_to_proxy_settings(
    proxies: list[Proxy],
) -> list[tuple[Proxy | None, ProxySettings | None]]:
    if settings.disable_proxies:
        return [(None, None)]

    try:
        return proxy_settings_internal(proxies)
    except ProxyCredentailException:
        if env_type == "local":
            return [(None, None)]
        raise
