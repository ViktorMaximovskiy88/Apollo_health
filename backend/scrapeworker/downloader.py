from contextlib import asynccontextmanager
import redis
import xxhash
import tempfile
import aiofiles
from random import choice
from backend.common.core.config import config
from playwright.async_api import APIResponse, Playwright, ProxySettings

from backend.scrapeworker.rate_limiter import RateLimiter

class DocDownloader():
    def __init__(self, playwright: Playwright):
        self.rate_limiter = RateLimiter()
        self.playwright = playwright
        self.redis = redis.from_url(
            config["REDIS_URL"],
            username='default',
            password=config["REDIS_PASSWORD"],
        )
        pass

    def skip_based_on_response(self, response: APIResponse):
        if not response.ok:
            return True
        return False

    @asynccontextmanager
    async def playwright_request_context(self, proxy: ProxySettings | None = None):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        }
        context = await self.playwright.request.new_context(extra_http_headers=headers, proxy=proxy)  # type: ignore
        try:
            yield context
        finally:
            await context.dispose()

    @asynccontextmanager
    async def download_url(self, url, proxies: list[ProxySettings | None] = []):
        async for attempt in self.rate_limiter.attempt_with_backoff():
            with attempt:
                proxy = choice(proxies)
                response: APIResponse | None = None
                async with self.playwright_request_context(proxy) as context:
                    response = await context.get(url)
                    if not response:
                        raise Exception(f"Failed to download url {url}")

                    print(f"Downloaded {url}, got {response.status}")
                    try:
                        yield response
                    finally:
                        await response.dispose()

    @asynccontextmanager
    async def tempfile_path(self, url: str, body: bytes):
        hash = xxhash.xxh128()
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                hash.update(body)
                await fd.write(body)
            yield temp.name, hash.hexdigest()


    async def download_to_tempfile(self, url: str, proxies: list[ProxySettings | None] = []):
        body = self.redis.get(url)
        if body == "DISCARD":
            return

        if body:
            print(f"Using cached {url}")
        else:
            print(f"Attempting download {url}")
            async with self.download_url(url, proxies) as response:
                if self.skip_based_on_response(response):
                    self.redis.set(url, "DISCARD", ex=60 * 60 * 1)  # 1 hour
                    return
                body = await response.body()
                self.redis.set(url, body, ex=60 * 60 * 1)  # 1 hour

        async with self.tempfile_path(url, body) as (temp_path, hash):
            yield temp_path, hash