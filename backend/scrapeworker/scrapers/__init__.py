from typing import Type

from backend.scrapeworker.scrapers.aspnet_webform import AspNetWebFormScraper
from backend.scrapeworker.scrapers.contentful_scraper import ContentfulScraper
from backend.scrapeworker.scrapers.direct_download import (
    DirectDownloadScraper,
    PlaywrightBaseScraper,
)

scrapers: list[Type[PlaywrightBaseScraper]] = [
    AspNetWebFormScraper,
    DirectDownloadScraper,
    ContentfulScraper,
]
