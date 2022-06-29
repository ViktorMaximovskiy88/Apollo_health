import pytest
from playwright.async_api import async_playwright
from backend.scrapeworker.drivers.playwright.base_driver import PlaywrightDriver
from backend.scrapeworker.drivers.playwright.direct_download import PlaywrightDirectDownload
from backend.scrapeworker.drivers.playwright.asp_web_form import PlaywrightAspWebForm

MOCK_HTML = "http://localhost:4040"

@pytest.mark.asyncio
async def test_playwright_driver_context():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        async with PlaywrightDriver(browser=browser, proxy=None) as driver:
            assert driver is not None


@pytest.mark.asyncio
async def test_playwright_driver_direct_download():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        async with PlaywrightDirectDownload(browser=browser, proxy=None) as driver:
            # fetch page
            await driver.nav_to_page(f"{MOCK_HTML}/direct-download/anchor.html")

            # mock selectors
            css_selector = "a[href]"
            elements = await driver.find_elements(css_selector)
            assert len(elements) == 1
            
            downloads = await driver.collect_downloads(elements=elements)
            assert len(downloads) == 1
            
            download = downloads[0]
            assert download.metadata.link_text == "Test anchor pdf"
            assert download.request.url == f"{MOCK_HTML}/direct-download/anchor.pdf"
            

@pytest.mark.asyncio
async def test_playwright_driver_webform():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        async with PlaywrightAspWebForm(browser=browser, proxy=None) as driver:
            # fetch page
            url = f"{MOCK_HTML}/web-form/post-back.html"
            await driver.nav_to_page(url)

            # mock selectors
            css_selector = 'a[href^="javascript:"]'
            elements = await driver.find_elements(css_selector)
            assert len(elements) == 3
            
            downloads = await driver.collect_downloads(elements=elements)
            assert len(downloads) == 3
            
            download = downloads[0]
            assert download.metadata.link_text == 'Do Post Back'
            assert download.request.method == 'POST'
            assert download.request.url == url
            assert download.request.data == "test=wtfbbq"
            assert len(download.request.headers.keys()) == 15
