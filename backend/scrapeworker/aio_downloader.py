import logging
import xxhash
import tempfile
import aiofiles
from contextlib import asynccontextmanager
from functools import cached_property
from typing import AsyncGenerator, Any
from aiohttp import ClientSession, ClientResponse, BasicAuth
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.models import Request
from backend.common.core.config import config
from playwright.async_api import ProxySettings
from tenacity import AttemptManager
from random import shuffle


class AioDownloader:

    session: ClientSession

    def __init__(self):
        self.session = ClientSession()

    async def close(self):
        await self.session.close()

    async def download_url(
        self, request: Request, proxies: list[tuple[Proxy | None, dict | None]] = []
    ):
        async for attempt, proxy in self.proxy_with_backoff(proxies):
            with attempt:
                response = None

                if request.method == "GET":
                    response = await self.get(request=request, proxy=proxy)
                else:
                    response = await self.post(equest=request, proxy=proxy)

                if not response:
                    raise Exception(f"Failed to download url {request.url}")

                print(f"Downloaded {request.url}, got {response.status}")
                yield response

    def convert_proxy(self, proxy: Proxy):
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

        return [proxy, proxies]

    @cached_property
    def proxies(self, proxies: list[Proxy]):
        _proxies = [self.convert_proxy(proxy) for proxy in proxies]
        return shuffle(_proxies)

    async def proxy_with_backoff(
        self, proxies: list[Proxy]
    ) -> AsyncGenerator[tuple[AttemptManager, dict[str, Any]], None]:
        shuffle(proxies)
        async for attempt in self.rate_limiter.attempt_with_backoff():
            i = attempt.retry_state.attempt_number - 1
            proxy_count = len(self.proxies)
            proxy, proxy_settings = (
                self.proxies[i % proxy_count] if proxy_count > 0 else [None, {}]
            )
            logging.info(
                f"{i} Using proxy {proxy and proxy.name} ({proxy_settings and proxy_settings['proxy']})"
            )
            yield attempt, proxy_settings

    async def get(self, request: Request, proxy: dict) -> bytes:
        response: ClientResponse
        async with self.session.get(
            request.url,
            data=request.data,
            headers=request.headers,
            proxy=proxy["proxy"],
            proxy_auth=proxy["proxy_auth"],
        ) as response:
            yield response

    async def post(self, request: Request, proxy: dict) -> bytes:
        response: ClientResponse
        async with self.session.post(
            request.url,
            data=request.data,
            headers=request.headers,
            proxy=proxy["proxy"],
            proxy_auth=proxy["proxy_auth"],
        ) as response:
            yield response

    @asynccontextmanager
    async def tempfile_path(self, body: bytes):
        hash = xxhash.xxh128()
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                hash.update(body)
                await fd.write(body)
            yield temp.name, hash.hexdigest()

    async def download_to_tempfile(
        self, url: str, proxies: list[tuple[Proxy | None, ProxySettings | None]] = []
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
                body = await response.body()
                # self.redis.set(url, body, ex=60 * 60 * 1)  # 1 hour

        async with self.tempfile_path(url, body) as (temp_path, hash):
            yield temp_path, hash
