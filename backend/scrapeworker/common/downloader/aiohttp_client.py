import logging
from aiohttp import ClientSession, ClientResponse
from backend.scrapeworker.common.models import Download, Request
from backend.scrapeworker.common.downloader.base import BaseDownloader

class AioDownloader(BaseDownloader):
    session: ClientSession
    def __init__(self): 
        self.session = ClientSession()

    async def close(self):
        await self.session.close()
    
    async def download(self, download: Download) -> tuple[str, str | None, str | None]:
        body: bytes
        filename: str | None
        file_ext: str | None = "pdf"

        if download.request.method == "POST":
            body, filename, file_ext = await self.post(download.request)
        else:
            body, filename, file_ext = await self.get(download.request)
        
        saved_filename, file_hash = await self.save_as_temp(body)

        return saved_filename, file_hash, file_ext
        
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

