from backend.scrapeworker.scrapers.aspnet_webform import (
    AspNetWebFormScraper,
)
from backend.scrapeworker.scrapers.direct_download import (
    DirectDownloadScraper,
)
from backend.scrapeworker.scrapers.direct_download import PlaywrightBaseScraper

scrapers: list[PlaywrightBaseScraper] = [
    AspNetWebFormScraper,
    DirectDownloadScraper,
]
