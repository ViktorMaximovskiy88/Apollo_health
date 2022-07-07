import logging
import xxhash
import tempfile
import aiofiles
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from aiohttp import ClientSession, ClientResponse, BasicAuth
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.models import Request
from backend.common.core.config import config
from playwright.async_api import ProxySettings
from tenacity import AttemptManager
from backend.scrapeworker.common.rate_limiter import RateLimiter
from random import shuffle

default_headers: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
}


class AioDownloader:

    session: ClientSession

    def __init__(self):
        self.session = ClientSession()
        self.rate_limiter = RateLimiter()

    async def close(self):
        await self.session.close()

    @asynccontextmanager
    async def download_url(
        self,
        request: Request,
        proxies: list[tuple[Proxy | None, dict | None]] = [],
    ):
        response: ClientResponse
        headers = default_headers | request.headers
        async for attempt, proxy in self.proxy_with_backoff(proxies):
            with attempt:
                response = await self.session.request(
                    url=request.url,
                    method=request.method,
                    headers=headers,
                    data=request.data,
                )
                if not response:
                    raise Exception(f"Failed to download url {request.url}")

                print(f"Downloaded {request.url}, got {response.status}")

        yield response

    # just return the aio useable proxy list
    def convert_proxy(self, proxy: Proxy) -> list[dict[str, str]]:
        proxy_auth = None
        proxies = []
        if proxy.credentials:
            username = config.get(proxy.credentials.username_env_var, None)
            password = config.get(proxy.credentials.password_env_var, None)
            if username and password:
                proxy_auth = BasicAuth(username, password)

        for endpoint in proxy.endpoints:
            proxies.append(
                {
                    "proxy": endpoint,
                    "proxy_auth": proxy_auth,
                }
            )

        return proxies

    def convert_proxies(
        self,
        proxies: list[tuple[Proxy | None, ProxySettings | dict[str, str] | None]] = [],
    ):
        _proxies = []
        for (proxy, _proxy_settings) in proxies:
            if proxy is not None:
                aio_proxies = self.convert_proxy(proxy)
                [_proxies.append((proxy, aio_proxy)) for aio_proxy in aio_proxies]
            else:
                [(None, None)]

        shuffle(_proxies)
        return _proxies

    async def proxy_with_backoff(
        self,
        proxies: list[tuple[Proxy | None, ProxySettings | dict[str, str] | None]] = [],
    ) -> AsyncGenerator[tuple[AttemptManager, dict[str, Any]], None]:
        aio_proxies = self.convert_proxies(proxies)
        async for attempt in self.rate_limiter.attempt_with_backoff():
            i = attempt.retry_state.attempt_number - 1
            proxy_count = len(aio_proxies)
            proxy, proxy_settings = (
                aio_proxies[i % proxy_count] if proxy_count > 0 else [None, {}]
            )
            logging.info(
                f"{i} Using proxy {proxy and proxy.name} ({proxy_settings and proxy_settings['proxy']})"
            )
            yield attempt, proxy_settings

    @asynccontextmanager
    async def tempfile_path(self, body: bytes):
        hash = xxhash.xxh128()
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                hash.update(body)
                await fd.write(body)
            yield temp.name, hash.hexdigest()

    async def download_to_tempfile(
        self,
        url: str,
        proxies: list[tuple[Proxy | None, ProxySettings | dict[str, str] | None]] = [],
    ):
        body = None  # self.redis.get(url)
        if body == "DISCARD":
            return

        if body:
            print(f"Using cached {url}")
        else:
            print(f"Attempting download {url}")
            async with self.download_url(url, proxies) as response:

                if not response.ok:
                    # self.redis.set(url, "DISCARD", ex=60 * 60 * 1)  # 1 hour
                    return
                body = await response.read()
                # self.redis.set(url, body, ex=60 * 60 * 1)  # 1 hour

        async with self.tempfile_path(body) as (temp_path, hash):
            yield temp_path, hash
