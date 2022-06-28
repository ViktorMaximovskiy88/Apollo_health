from aiofiles import open
from aiohttp import ClientSession
from backend.scrapeworker.common.models import Download
import re

def get_attachment_filename(header_value: str):
    match = re.search('filename="(.*)"', header_value)
    return match.group(1)

async def post(download: Download):
    async with ClientSession() as session:
        async with session.post(
            download.request.url,
            data=download.request.data,
            headers=download.request.headers
        ) as response:
                
            if response.status != 200:
                return
            
            filename=download.metadata.text
            if response.headers['Content-Disposition']:
                filename = get_attachment_filename(response.headers['Content-Disposition'])
                        
            body = await response.read()
            async with open(f'./{filename}', "wb") as out:
                await out.write(body)
                await out.flush()
