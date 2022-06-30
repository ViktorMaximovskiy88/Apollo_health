import pytest

# from playwright.async_api import async_playwright
# from backend.scrapeworker.drivers.playwright.direct_download import (
#     PlaywrightDirectDownload,
# )
# from backend.scrapeworker.common.models import Download
# from backend.scrapeworker.strategies.direct_download import DirectDownloadStategy
# from backend.common.models.site import ScrapeMethodConfiguration

# MOCK_HTML = "http://localhost:4040"


@pytest.mark.asyncio
async def test_playwright_direct_download_strategy():
    pass
    # async with async_playwright() as playwright:
    #     browser = await playwright.chromium.launch()
    #     async with PlaywrightDirectDownload(browser=browser, proxy=None) as driver:
    #         config = ScrapeMethodConfiguration(
    #             document_extensions=["pdf"],
    #             url_keywords=["keyword"],
    #         )

    #         strategy = DirectDownloadStategy(config=config, driver=driver)
    #         elements, downloads = await strategy.execute(
    #             f"{MOCK_HTML}/direct-download/extension-keyword.html"
    #         )

    #         assert len(downloads) == 2

    #         assert downloads[0].metadata.link_text == "Extension match"
    #         assert downloads[0].request.url == f"{MOCK_HTML}/direct-download/anchor.pdf"

    #         assert downloads[1].metadata.link_text == "Keyword match"
    #         assert downloads[1].request.url == f"{MOCK_HTML}/direct-download/keyword"
