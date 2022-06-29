import pytest
from backend.scrapeworker.common.downloader.aiohttp_client import AioDownloader
from backend.scrapeworker.common.models import Download, Metadata, Request

MOCK_SERVER = "http://localhost:4040"

@pytest.mark.asyncio
async def test_aiodownloader_get():

    test_one = Download(
        metadata=Metadata(
            text="test one"
        ),
        request=Request(
            url=f'{MOCK_SERVER}/data/test-one.pdf'
        ),
    )

    downloader = AioDownloader()
    proxies = []
    
    async for (temp_path, checksum, file_ext) in downloader.download(
        test_one, proxies
    ):
        assert checksum == "905bc67005486d6a7b38b3ef27e8728f"
        assert file_ext == "pdf"

        await downloader.close()