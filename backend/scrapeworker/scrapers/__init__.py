from typing import Type

from backend.scrapeworker.scrapers.aspnet_webform import AspNetWebFormScraper
from backend.scrapeworker.scrapers.direct_download import (
    DirectDownloadScraper,
    PlaywrightBaseScraper,
)
from backend.scrapeworker.scrapers.javascript_click import JavascriptClick

scrapers: list[Type[PlaywrightBaseScraper]] = [
    AspNetWebFormScraper,
    DirectDownloadScraper,
    JavascriptClick,
]
