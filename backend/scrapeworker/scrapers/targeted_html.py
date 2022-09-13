import asyncio
import logging
from copy import copy
from functools import cached_property

from bs4 import BeautifulSoup, PageElement
from playwright.async_api import Locator

from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_full_text
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.scrapers.playwright_base_scraper import (
    PlaywrightBaseScraper,
    closest_heading_expression,
)


class TargetedHtmlScraper(PlaywrightBaseScraper):
    type = "TargetedHTML"
    doc_client = DocumentStorageClient()

    @cached_property
    def css_selector(self) -> str | None:
        css_selectors = []
        return ",".join(css_selectors)

    @cached_property
    def xpath_selector(self) -> str:
        selectors = []
        for attr_selector in self.config.html_attr_selectors:
            selectors.append(to_xpath(attr_selector))
        selector_string = "|".join(selectors)
        self.log.info(selector_string)
        return selector_string

    def __add_default_tags(self, soup: BeautifulSoup):
        """Add <html> and <body> tags to soup if either are absent."""

        def add_children(parent: list[PageElement], target: PageElement):
            for child in parent:
                child_copy = copy(child)
                target.append(child_copy)

        new_soup = BeautifulSoup("<html></html>", features="html.parser")
        assert new_soup.html is not None
        html_element = soup.html
        body_element = soup.body
        if not html_element and not body_element:
            body_element = new_soup.new_tag("body")
            add_children(soup.contents, body_element)
            new_soup.html.append(body_element)
        elif not html_element:
            add_children(soup.contents, new_soup.html)
        elif not body_element:
            body_element = new_soup.new_tag("body")
            add_children(html_element.contents, body_element)
            new_soup.html.append(body_element)
        else:
            new_soup = soup

        return new_soup

    def clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, features="html.parser")
        for selector in self.config.html_exclusion_selectors:
            attrs = {}
            attrs[selector.attr_name] = (
                selector.attr_value if selector.attr_value is not None else True
            )
            remove_elements = soup.find_all(
                selector.attr_element, attrs=attrs, string=selector.has_text
            )
            for element in remove_elements:
                element.extract()

        clean_soup = self.__add_default_tags(soup)
        return str(clean_soup)

    async def extract_metadata(self, element: Locator) -> Metadata:
        closest_heading: str | None

        element_id, closest_heading = await asyncio.gather(
            element.get_attribute("id"),
            element.evaluate(closest_heading_expression),
        )

        if closest_heading:
            closest_heading = closest_heading.strip()

        return Metadata(
            element_id=element_id,
            closest_heading=closest_heading,
            playbook_context=self.playbook_context,
        )

    async def scrape_and_queue(self, downloads: list[DownloadContext]) -> None:
        xpath_locator = self.page.locator(self.xpath_selector)
        xpath_locator_count = await xpath_locator.count()

        for index in range(0, xpath_locator_count):
            try:
                html_locator = xpath_locator.nth(index)
                metadata = await self.extract_metadata(html_locator)
                html_content = await html_locator.inner_html()
                cleaned_html = self.clean_html(html_content)
                checksum = hash_full_text(cleaned_html)
                dest_path = f"{checksum}.html"
                # if not self.doc_client.object_exists(dest_path):
                bytes_obj = bytes(cleaned_html, "iso-8859-1")
                self.doc_client.write_object_mem(dest_path, bytes_obj)
                filename = metadata.closest_heading  # something better?
                if not filename:
                    filename = await self.page.title()
                downloads.append(
                    DownloadContext(
                        direct_scrape=True,
                        metadata=metadata,
                        file_extension="html",
                        file_hash=checksum,
                        request=Request(url=self.page.url, filename=filename),
                    )
                )
            except Exception:
                logging.error("exception", exc_info=True)
                await self.page.goto(self.url)

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []
        await self.scrape_and_queue(downloads)
        return downloads
