from urllib.parse import ParseResult, urlparse

from playwright.async_api import Request as PlaywrightRequest
from playwright.async_api import Route

from backend.scrapeworker.scrapers.direct_download import DirectDownloadScraper


class HorizonBlueScraper(DirectDownloadScraper):
    type: str = "HorizonBlue"

    @staticmethod
    def scrape_select(url, config: None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        result = parsed_url.netloc == "www.horizonblue.com"
        return result

    @staticmethod
    def page_route(route: Route, request: PlaywrightRequest):
        if request.url.startswith(
            "https://www.horizonblue.com/Dismall-liue-due-as-the-for-very-his-good-implor"
        ):
            return route.abort()
        else:
            return route.continue_()
