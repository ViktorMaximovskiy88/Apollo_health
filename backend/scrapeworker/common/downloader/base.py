import re

from tempfile import NamedTemporaryFile
from xxhash import xxh128
from aiofiles import open
from backend.scrapeworker.common.models import Download, Request

class BaseDownloader:
    def fetch(self, download: Download):
        pass
    
    def get(self, request: Request):
        pass

    def post(self, request: Request):
        pass
    
    async def save_as_temp(self, body: bytes) -> tuple[str, str | None]:
        hash = xxh128()
        with NamedTemporaryFile(delete=False) as temp:
            async with open(temp.name, "wb") as fd:
                hash.update(body)
                await fd.write(body)
                await fd.flush()
            
            return temp.name, hash.hexdigest()

    async def save_as(self, filename: str, body: bytes) -> tuple[str, str | None]:
        async with open(f'./{filename}', "wb") as fd:
            await fd.write(body)
            await fd.flush()

        return filename, None

    # TODO get file ext if we have one
    def get_attachment_filename(header_value: str) -> tuple[str, str | None]:
        match = re.search('filename="(.*)"', header_value)
        return match.group(1), None
