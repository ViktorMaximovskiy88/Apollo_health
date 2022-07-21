from dataclasses import dataclass
import logging
from ssl import SSLContext
import tempfile
import ssl
import aiofiles
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from aiohttp import ClientSession, ClientResponse, BasicAuth, TCPConnector
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.models import Download
from backend.common.core.config import config
from playwright.async_api import ProxySettings
from tenacity import AttemptManager
from backend.scrapeworker.common.rate_limiter import RateLimiter
from random import shuffle
from backend.common.storage.hash import DocStreamHasher

default_headers: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
}

@dataclass
class AioProxy:
    proxy: str
    proxy_auth: BasicAuth | None


class AioDownloader:

    session: ClientSession

    def __init__(self):
        self.session = ClientSession(connector=TCPConnector(ssl=self.permissive_ssl_context()))
        self.rate_limiter = RateLimiter()
    
    def permissive_ssl_context(self):
        context = SSLContext()
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        ciphers = context.get_ciphers()
        all_ciphers = ':'.join(c['name'] for c in ciphers) + ':HIGH:!DH:!aNULL'
        context.set_ciphers(all_ciphers)

        return context

    async def close(self):
        await self.session.close()

    @asynccontextmanager
    async def download_url(
        self,
        download: Download,
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ):
        response: ClientResponse | None = None
        headers = default_headers | download.request.headers
        async for attempt, proxy in self.proxy_with_backoff(proxies):
            with attempt:
                # TODO de-duplicate this...
                if proxy:
                    response = await self.session.request(
                        url=download.request.url,
                        method=download.request.method,
                        headers=headers,
                        data=download.request.data,
                        proxy=proxy.proxy,
                        proxy_auth=proxy.proxy_auth,
                    )
                else:
                    response = await self.session.request(
                        url=download.request.url,
                        method=download.request.method,
                        headers=headers,
                        data=download.request.data,
                    )

                download.response.status = response.status
                logging.info(
                    f"Downloaded {download.request.url}, got {response.status}"
                )

                yield response
        
    # just return the aio useable proxy list
    def convert_proxy(self, proxy: Proxy) -> list[AioProxy]:
        proxy_auth = None
        proxies: list[AioProxy] = []
        if proxy.credentials:
            username = config.get(proxy.credentials.username_env_var, None)
            password = config.get(proxy.credentials.password_env_var, None)
            if username and password:
                proxy_auth = BasicAuth(username, password)

        for endpoint in proxy.endpoints:
            proxies.append(
                AioProxy(
                    proxy=f"http://{endpoint}",
                    proxy_auth=proxy_auth,
                )
            )

        return proxies

    def convert_proxies(
        self,
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ) -> list[tuple[Proxy | None, AioProxy | None]]:
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
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ) -> AsyncGenerator[tuple[AttemptManager, AioProxy | None], None]:
        aio_proxies = self.convert_proxies(proxies)
        async for attempt in self.rate_limiter.attempt_with_backoff():
            i = attempt.retry_state.attempt_number - 1
            proxy_count = len(aio_proxies)
            proxy, proxy_settings = (
                aio_proxies[i % proxy_count] if proxy_count > 0 else (None, None)
            )
            logging.info(
                f"{i} Using proxy {proxy and proxy.name} ({proxy_settings and proxy_settings.proxy})"
            )
            yield attempt, proxy_settings

    @asynccontextmanager
    async def tempfile_path(self, download: Download, response: ClientResponse):
        download.guess_extension()
        hasher = DocStreamHasher()
        with tempfile.NamedTemporaryFile(suffix=f".{download.file_extension}") as temp:
            download.file_path = temp.name
            async with aiofiles.open(download.file_path, "wb") as fd:
                async for data in response.content.iter_any():
                    await fd.write(data)
                    hasher.update(data)
                await fd.flush()

            download.file_hash = hasher.hexdigest()
            yield download.file_path, download.file_hash

    async def download_to_tempfile(
        self,
        download: Download,
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ):
        url = download.request.url
        logging.info(f"Attempting download {url}")
        async with self.download_url(download, proxies) as response:
            if not response.ok:
                return

            download.response.from_headers(response.headers)

            async with self.tempfile_path(download, response) as (temp_path, hash):
                yield temp_path, hash
