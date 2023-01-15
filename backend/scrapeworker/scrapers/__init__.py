import re
from logging import Logger
from typing import Type
from urllib.parse import urlparse

from playwright.async_api import BrowserContext, Page

from backend.common.core.enums import ScrapeMethod
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.playbook import PlaybookContext
from backend.scrapeworker.scrapers.aspnet_webform import AspNetWebFormScraper
from backend.scrapeworker.scrapers.by_domain.formulary_navigator import FormularyNavigatorScraper
from backend.scrapeworker.scrapers.by_domain.humana import HumanaScraper
from backend.scrapeworker.scrapers.by_domain.tricare import TricareScraper
from backend.scrapeworker.scrapers.direct_download import (
    DirectDownloadScraper,
    PlaywrightBaseScraper,
)
from backend.scrapeworker.scrapers.javascript_click import JavascriptClick
from backend.scrapeworker.scrapers.targeted_html import TargetedHtmlScraper

scrapers: list[Type[PlaywrightBaseScraper]] = [
    AspNetWebFormScraper,
    DirectDownloadScraper,
    JavascriptClick,
    TargetedHtmlScraper,
    HumanaScraper,
    FormularyNavigatorScraper,
    TricareScraper,
]


class ScrapeHandler:
    def __init__(
        self,
        context: BrowserContext,
        page: Page,
        playbook_context: PlaybookContext,
        log: Logger,
        config: ScrapeMethodConfiguration,
        scrape_method: ScrapeMethod | None = None,
    ) -> None:
        self.context = context
        self.page = page
        self.playbook_context = playbook_context
        self.log = log
        self.config = config
        self.scrape_method = scrape_method

    def __is_google(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.hostname in ["drive.google.com", "docs.google.com"]

    def __get_google_id(self, url: str) -> str:
        matched = re.search(r"/d/(.*)/", url)
        if not matched:
            raise Exception(f"{url} is not a valid google doc/drive url")
        return matched.group(1)

    def __preprocess_download(
        self, download: DownloadContext, base_url: str, metadata: dict
    ) -> None:
        for key in metadata:
            download.__setattr__(key, metadata[key])
        download.metadata.base_url = base_url
        if self.__is_google(download.request.url):
            google_id = self.__get_google_id(download.request.url)
            download.request.url = f"https://drive.google.com/u/0/uc?id={google_id}&export=download"

    async def run_scrapers(
        self, url: str, base_url: str, downloads: list[DownloadContext], metadata: dict = {}
    ) -> None:
        for Scraper in scrapers:
            scraper = Scraper(
                page=self.page,
                context=self.context,
                config=self.config,
                playbook_context=self.playbook_context,
                url=url,
                log=self.log,
                metadata=metadata,
                scrape_method=self.scrape_method,
            )

            if not await scraper.is_applicable():
                continue

            is_searchable = metadata.get("is_searchable", False)

            for download in await scraper.execute():
                download.is_searchable = is_searchable
                self.log.debug(f"downloads ... {base_url} {download.request.url}")
                self.__preprocess_download(download, base_url, metadata)
                downloads.append(download)
