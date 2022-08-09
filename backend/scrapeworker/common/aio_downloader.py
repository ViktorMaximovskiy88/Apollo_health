import logging
import ssl
import tempfile
from dataclasses import dataclass
from random import shuffle
from ssl import SSLContext
from typing import AsyncGenerator

import aiofiles
from aiohttp import BasicAuth, ClientResponse, ClientSession, TCPConnector
from playwright.async_api import ProxySettings
from tenacity import AttemptManager

from backend.common.core.config import config
from backend.common.models.proxy import Proxy
from backend.common.models.site_scrape_task import InvalidResponse, ValidResponse
from backend.common.storage.hash import DocStreamHasher
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.common.rate_limiter import RateLimiter

default_headers: dict[str, str] = {
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",  # noqa
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
        all_ciphers = ":".join(c["name"] for c in ciphers) + ":HIGH:!DH:!aNULL"
        context.set_ciphers(all_ciphers)

        return context

    async def close(self):
        await self.session.close()

    async def send_request(self, download: DownloadContext, proxy: AioProxy | None):
        headers = default_headers | download.request.headers
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
        logging.info(f"Downloaded {download.request.url}, got {response.status}")
        return response

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
                f"{i} Using proxy {proxy and proxy.name} ({proxy_settings and proxy_settings.proxy})"  # noqa E501
            )
            yield attempt, proxy_settings

    async def write_response_to_file(
        self,
        download: DownloadContext,
        response: ClientResponse,
        temp: tempfile._TemporaryFileWrapper,
    ):
        hasher = DocStreamHasher()
        download.file_path = temp.name

        async with aiofiles.open(download.file_path, "wb") as fd:
            async for data in response.content.iter_any():
                await fd.write(data)
                hasher.update(data)
            await fd.flush()

        download.set_mimetype()
        download.set_extension_from_mimetype()
        download.file_hash = hasher.hexdigest()

        return download.file_path, download.file_hash

    async def try_download_to_tempfile(
        self,
        download: DownloadContext,
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ):
        url = download.request.url
        logging.info(f"Attempting download {url}")

        async for attempt, proxy in self.proxy_with_backoff(proxies):
            with attempt:
                response = await self.send_request(download, proxy)

                download.response.from_aio_response(response)

                # how to identity proxy error vs site error...
                if not response.ok:
                    invalid_response = InvalidResponse(
                        proxy_url=proxy.proxy, **download.response.dict()
                    )
                    download.invalid_responses.append(invalid_response)
                    logging.error(invalid_response)
                    continue

                download.valid_response = ValidResponse(
                    proxy_url=proxy.proxy, **download.response.dict()
                )
                # We only need this now due to the xlsx lib needing an ext (derp)
                # TODO see if we can unhave this; the excel lib is dumb
                download.guess_extension()

                with tempfile.NamedTemporaryFile(suffix=f".{download.file_extension}") as temp:
                    yield await self.write_response_to_file(download, response, temp)
