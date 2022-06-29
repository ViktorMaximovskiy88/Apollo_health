import pytest
from backend.scrapeworker.downloader import DocDownloader
from backend.common.storage.hash import hash_bytes, hash_full_text, get_document_hash
from backend.common.storage.text_extraction import TextExtractor
import requests
import tempfile
import aiofiles
import aiofiles.os

@pytest.mark.asyncio
async def test_html_hash():
    URL = "https://parprdusemmitst01.blob.core.windows.net/autohunteddocs/1e7a028b-c1ef-4472-9b5a-01213ea47ebd/1e7a028b-c1ef-4472-9b5a-01213ea47ebd.htm"
    response = requests.get(URL)
    extractor = TextExtractor(document_bytes=response.content,
                            mimetype=None)
    await extractor.extract()
    full_text = extractor.full_text     
    hash=get_document_hash(extractor)
    assert hash == "94be9fbbe972308a65bed0efcdf1ba3d"



@pytest.mark.asyncio
async def test_pdf_hash():
    URL = "https://parprdusemmitst01.blob.core.windows.net/autohunteddocs/7c8418d4-054b-4fa4-9b97-d3f75c353dd1/7c8418d4-054b-4fa4-9b97-d3f75c353dd1.pdf"
    response = requests.get(URL)
    with tempfile.NamedTemporaryFile() as temp:
             async with aiofiles.open(temp.name, "wb") as fd:
                
                res = await fd.write(response.content)
                await aiofiles.os.stat(str(temp.name))
                extractor = TextExtractor(document_bytes=response.content,
                                        mimetype=None, temp_path=temp.name)
                await extractor.extract()
                full_text = extractor.full_text
                hash=get_document_hash(extractor)
                assert hash == "f569ad67d959430a55870e04be4c7ed2"

