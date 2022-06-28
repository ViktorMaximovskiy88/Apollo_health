import pytest
from backend.scrapeworker.common.downloader.aiohttp_client import AioDownloader
from backend.scrapeworker.common.models import Download, Metadata, Request

MOCK_SERVER = "http://localhost:4040"

@pytest.mark.asyncio
async def test_aiodownloader_get_success():

    test_one = Download(
        metadata=Metadata(
            text="test one"
        ),
        request=Request(
            url=f'{MOCK_SERVER}/data/test-one.pdf'
        ),
    )

    async with AioDownloader() as downloader:
        saved_filename, file_hash, file_ext = await downloader.download(test_one)
        assert True == True
