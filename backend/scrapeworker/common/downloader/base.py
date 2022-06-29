import re

from tempfile import NamedTemporaryFile
from xxhash import xxh128
from aiofiles import open
from backend.scrapeworker.common.models import Download, Request
from backend.scrapeworker.common.rate_limiter import RateLimiter        
        
class BaseDownloader:
    rate_limiter: RateLimiter
    def __init__(self):
        self.rate_limiter = RateLimiter()
        
    def download(self, download: Download):
        pass
    
    def get(self, request: Request):
        pass

    def post(self, request: Request):
        pass
    
    @property
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        }        
    
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
