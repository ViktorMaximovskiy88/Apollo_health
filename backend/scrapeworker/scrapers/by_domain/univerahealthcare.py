from urllib.parse import ParseResult, urlparse

from playwright.async_api import Request as PlaywrightRequest
from playwright.async_api import Route

from backend.scrapeworker.scrapers.direct_download import DirectDownloadScraper


class UniveraHealthcareScraper(DirectDownloadScraper):
    type: str = "UniveraHealthcare"

    @staticmethod
    def scrape_select(url, config: None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        result = parsed_url.netloc == "medicare.univerahealthcare.com"
        return result

    @staticmethod
    def page_route(route: Route, request: PlaywrightRequest):
        if request.url.startswith(
            "https://medicare.univerahealthcare.com/g-Enters-country-Sword-a-made-to-did-lease-he-lo"  # noqa
        ):
            return route.abort()
        else:
            return route.continue_()
