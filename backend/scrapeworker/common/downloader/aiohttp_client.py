import logging
from functools import cached_property
from typing import AsyncGenerator, Any
from aiohttp import ClientSession, ClientResponse, BasicAuth
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.models import Download, Request
from backend.scrapeworker.common.downloader.base import BaseDownloader
from backend.common.core.config import config
from tenacity import AttemptManager
from random import shuffle

# TODO decouple http client with downloader concept
class AioDownloader(BaseDownloader):
    session: ClientSession
    def __init__(self): 
        super().__init__()
        self.session = ClientSession()

    async def close(self):
        await self.session.close()

    def convert_proxy(self, proxy: Proxy):
        proxy_auth=None
        proxies = []
        if proxy.credentials:
            username = config.get(proxy.credentials.username_env_var, None)
            password = config.get(proxy.credentials.password_env_var, None)
            if username and password:
                proxy_auth = BasicAuth(username, password)

        for endpoint in proxy.endpoints:
            proxies.append({
                'proxy': endpoint,
                'proxy_auth': proxy_auth,
            })

        return [proxy, proxies]
        
    @cached_property
    def proxies (self, proxies: list[Proxy]):
        _proxies = [ self.convert_proxy(proxy) for proxy in proxies ]
        return shuffle(_proxies)
    
    async def proxy_with_backoff(self, proxies: list[Proxy]) -> AsyncGenerator[tuple[AttemptManager, dict[str, Any]], None]:
        self.proxies = proxies
        async for attempt in self.rate_limiter.attempt_with_backoff():
            i = attempt.retry_state.attempt_number - 1
            proxy_count = len(self.proxies)
            proxy, proxy_settings = self.proxies[i % proxy_count] if proxy_count > 0 else [None, {}]
            logging.info(
                f"{i} Using proxy {proxy and proxy.name} ({proxy_settings and proxy_settings['proxy']})"
            )
            yield attempt, proxy_settings    
    
    async def download(self, download: Download, proxies: list[Proxy]) -> tuple[str, str | None, str | None]:
        body: bytes
        filename: str | None
        file_ext: str | None = "pdf"

        async for attempt, proxy_settings in self.proxy_with_backoff(proxies):
            with attempt:
                if download.request.method == "POST":
                    body, filename, file_ext = await self.post(download.request, **proxy_settings)
                else:
                    body, filename, file_ext = await self.get(download.request, **proxy_settings)
                
                saved_filename, file_hash = await self.save_as_temp(body)

                yield saved_filename, file_hash, file_ext
        
    # lower order method
    async def get(self, request: Request) -> tuple[bytes, str]:
        response: ClientResponse
        async with self.session.get(
            request.url,
            headers=request.headers
        ) as response:
            return await self.__handle_response(response)

    # lower order method
    async def post(self, request: Request) -> bytes:        
        response: ClientResponse
        async with self.session.post(
            request.url,
            data=request.data,
            headers=request.headers
        ) as response:            
            return await self.__handle_response(response)
            
    async def __handle_response(self, response: ClientResponse) ->  tuple[bytes, str | None, str | None]:
        filename: str | None = "test"
        file_ext: str | None = "pdf"

        if response.headers.get('Content-Disposition'):
            filename, file_ext = self.get_attachment_filename(response.headers['Content-Disposition'])
        
        if response.status == 200:
            body = await response.read()
            return body, filename, file_ext        

