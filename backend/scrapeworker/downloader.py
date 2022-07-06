import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import redis
import xxhash
import tempfile
import aiofiles
import pathlib
import os
from random import shuffle
from backend.common.core.config import config
from playwright.async_api import (
    APIResponse,
    APIRequestContext,
    Playwright,
    ProxySettings,
)
from backend.scrapeworker.rate_limiter import RateLimiter
from backend.common.models.proxy import Proxy
from backend.scrapeworker.rate_limiter import RateLimiter
from tenacity import AttemptManager
from tenacity._asyncio import AsyncRetrying


class DocDownloader:
    def __init__(self, playwright: Playwright):
        self.rate_limiter = RateLimiter()
        self.playwright = playwright
        # self.redis = redis.from_url(
        # config["REDIS_URL"],
        # username='default',
        # password=config["REDIS_PASSWORD"],
        # )

    def skip_based_on_response(self, response: APIResponse) -> bool:
        if not response.ok:
            return True
        return False

    async def playwright_request_context(
        self, proxy: ProxySettings | None = None
    ) -> APIRequestContext:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        }
        context = await self.playwright.request.new_context(extra_http_headers=headers, proxy=proxy, ignore_https_errors=True)  # type: ignore
        return context

    async def proxy_with_backoff(
        self, proxies: list[tuple[Proxy | None, ProxySettings | None]]
    ) -> AsyncGenerator[tuple[AttemptManager, ProxySettings | None], None]:
        shuffle(proxies)
        async for attempt in self.rate_limiter.attempt_with_backoff():
            i = attempt.retry_state.attempt_number - 1
            n_proxies = len(proxies)
            proxy, proxy_settings = proxies[i % n_proxies]
            print(
                f"{i} Using proxy {proxy and proxy.name} ({proxy_settings and proxy_settings.get('server')})"
            )
            yield attempt, proxy_settings

    @asynccontextmanager
    async def download_url(
        self, url, proxies: list[tuple[Proxy | None, ProxySettings | None]] = []
    ):
        context: APIRequestContext | None = None
        response: APIResponse | None = None
        async for attempt, proxy in self.proxy_with_backoff(proxies):
            with attempt:
                context = await self.playwright_request_context(proxy)
                response = await context.get(url)
                if not response:
                    raise Exception(f"Failed to download url {url}")

        if not response:
            raise Exception(f"Failed to download url {url}")

        print(f"Downloaded {url}, got {response.status}")
        try:
            yield response
        finally:
            if context:
                await context.dispose()

    @asynccontextmanager
    async def tempfile_path(self, url: str, body: bytes):
        hash = xxhash.xxh128()
        guess_suffix = pathlib.Path(os.path.basename(url)).suffix
        with tempfile.NamedTemporaryFile(suffix=guess_suffix) as temp:
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
                if self.skip_based_on_response(response):
                    # self.redis.set(url, "DISCARD", ex=60 * 60 * 1)  # 1 hour
                    return
                body = await response.body()
                # self.redis.set(url, body, ex=60 * 60 * 1)  # 1 hour

        async with self.tempfile_path(url, body) as (temp_path, hash):
            yield temp_path, hash
