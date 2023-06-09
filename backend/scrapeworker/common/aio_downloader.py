import os
import ssl
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http.cookies import CookieError, Morsel
from random import shuffle
from ssl import SSLContext
from typing import AsyncGenerator, Coroutine

import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader
from aiohttp import BasicAuth, ClientHttpProxyError, ClientResponse, ClientSession, TCPConnector
from playwright.async_api import ProxySettings
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from backend.common.core.config import config
from backend.common.models.link_task_log import InvalidResponse, ValidResponse
from backend.common.models.proxy import Proxy
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import DocStreamHasher
from backend.common.storage.s3_client import AsyncS3Client
from backend.scrapeworker.common.models import DownloadContext

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

    def __init__(self, doc_client: DocumentStorageClient | AsyncS3Client, log, scrape_temp_path):
        self.doc_client = doc_client
        self.log = log
        self.session = ClientSession(connector=TCPConnector(ssl=self.permissive_ssl_context()))
        self.scrape_temp_path = scrape_temp_path

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
        self.log.info("Before attempting downloader close")
        await self.session.close()
        self.log.info("After attempting downloader close")

    def valid_cookie(self, cookie):
        """
        Check if cookie is valid for Morsel. This is the same check used by aiohttp,
        we repeat it here so we can catch the exception and exclude the key.
        """

        if "name" not in cookie or "value" not in cookie:
            return False

        try:
            Morsel().set(cookie["name"], cookie["value"], None)
        except CookieError:
            return False

        return True

    async def send_request(self, download: DownloadContext, proxy: AioProxy | None):
        headers = default_headers | download.request.headers

        cookies = {}
        for cookie in download.request.cookies:
            if self.valid_cookie(cookie):
                cookies[cookie["name"]] = cookie["value"]  # type: ignore

        if proxy:
            response = await self.session.request(
                url=download.request.url,
                method=download.request.method,
                headers=headers,
                cookies=cookies,
                data=download.request.data,
                proxy=proxy.proxy,
                proxy_auth=proxy.proxy_auth,
            )
        else:
            response = await self.session.request(
                url=download.request.url,
                method=download.request.method,
                headers=headers,
                cookies=cookies,
                data=download.request.data,
            )

        download.response.status = response.status
        self.log.info(f"Downloaded {download.request.url}, got {response.status}")
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

    def get_shuffled_proxies(
        self,
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ) -> tuple[list[tuple[Proxy | None, AioProxy | None]], int]:
        _proxies = []
        for (proxy, _proxy_settings) in proxies:
            if proxy:
                aio_proxies = self.convert_proxy(proxy)
                [_proxies.append((proxy, aio_proxy)) for aio_proxy in aio_proxies]

        shuffle(_proxies)
        return _proxies, len(_proxies)

    async def set_download_data(self, download: DownloadContext, path: str) -> None:
        download.file_path = path
        if not download.mimetype:
            download.set_mimetype()
        # NOTE always set via the file; we cant trust downloads in many cases
        download.set_extension_from_mimetype()
        # NOTE always set file size
        download.file_size = os.path.getsize(download.file_path)

    async def write_response_to_file(
        self,
        download: DownloadContext,
        response: ClientResponse,
        temp: AsyncBufferedReader,
    ):
        hasher = DocStreamHasher()

        async with aiofiles.open(temp.name, "wb") as fd:
            async for data in response.content.iter_any():
                await fd.write(data)
                hasher.update(data)
            await fd.flush()

        await self.set_download_data(download, str(temp.name))

        download.file_hash = hasher.hexdigest()
        self.log.info(f"mimetype={download.mimetype} file_hash={download.file_hash}")  # noqa
        return download.file_path, download.file_hash

    async def open_direct_scrape(self, key: str, temp: AsyncBufferedReader):
        doc = self.doc_client.read_object(key)
        if isinstance(doc, Coroutine):
            doc = await doc

        await temp.write(doc)
        await temp.seek(0)

    @asynccontextmanager
    async def try_download_to_tempfile(
        self,
        download: DownloadContext,
        proxies: list[tuple[Proxy | None, ProxySettings | None]] = [],
    ) -> AsyncGenerator[tuple[str | None, str | None], None]:

        url = download.request.url
        if download.direct_scrape:
            self.log.debug(f"Before direct_scrape download {url}")
            dest_path = f"{download.file_hash}.{download.file_extension}"
            async with aiofiles.tempfile.NamedTemporaryFile(dir=self.scrape_temp_path) as temp:
                await self.open_direct_scrape(dest_path, temp)
                await self.set_download_data(download, str(temp.name))
                self.log.debug(
                    f"mimetype={download.mimetype} file_hash={download.file_hash}"
                )  # noqa
                yield download.file_path, download.file_hash
        elif download.file_path and download.playwright_download:
            self.log.debug(f"Before playwright_download download {url}")
            await self.set_download_data(download, download.file_path)
            self.log.info(f"mimetype={download.mimetype} file_hash={download.file_hash}")  # noqa
            yield download.file_path, download.file_hash
        else:
            self.log.debug(f"Before retry download {url}")
            response: ClientResponse | None = None
            proxy_url = None
            aio_proxies, proxy_count = self.get_shuffled_proxies(proxies)
            retries = 3 * proxy_count if proxy_count else 3
            result = (None, None)
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(retries),
                wait=wait_random(min=1, max=5),
                reraise=True,
            ):
                with attempt:
                    attempt_number = attempt.retry_state.attempt_number
                    self.log.info(
                        f"Attempt #{attempt_number} idle={attempt.retry_state.idle_for} url={url}"
                    )
                    index = attempt_number - 1

                    _proxy_record, proxy = (
                        aio_proxies[index % proxy_count] if proxy_count else [None, None]
                    )

                    async with aiofiles.tempfile.NamedTemporaryFile(
                        dir=self.scrape_temp_path
                    ) as temp:
                        proxy_url = proxy.proxy if proxy else None

                        try:
                            response = await self.send_request(download, proxy)
                            download.response.from_aio_response(response)
                            self.log.info(f"Attempting download {url} response")
                        except ClientHttpProxyError as proxy_error:
                            self.log.error(f"Client Proxy Error AIO {url}")
                            download.invalid_responses.append(
                                InvalidResponse(
                                    proxy_url=proxy_url,
                                    status=proxy_error.status,
                                    message=proxy_error.message,
                                )
                            )
                            raise proxy_error

                        self.log.debug(f"Before link log {url} response")

                        if not (response and response.ok):
                            invalid_response = InvalidResponse(
                                proxy_url=proxy_url, **download.response.dict()
                            )
                            download.invalid_responses.append(invalid_response)
                            self.log.error(invalid_response)
                            raise Exception("invalid response but lets retry ¯\\_(ツ)_/¯")
                        else:
                            download.valid_response = ValidResponse(
                                proxy_url=proxy_url, **download.response.dict()
                            )

                            # We only need this now due to the xlsx lib needing an ext (derp)
                            # TODO see if we can unhave this; the excel lib is dumb
                            download.guess_extension()
                            result = await self.write_response_to_file(download, response, temp)
                            yield result
