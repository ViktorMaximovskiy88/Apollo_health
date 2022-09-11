import asyncio
import logging
from functools import cached_property

from bs4 import BeautifulSoup
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

    def remove_exclusions(self, html: str) -> str:
        soup = BeautifulSoup(html, features="html.parser")
        new_soup = BeautifulSoup("", features="html.parser")
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

        # TODO: conditionally add html and body tags
        # new_soup = soup("<html/>")
        # if no html tag and no body
        # append body to new soup,
        # add everything to new body tag.

        # if no html
        # add everything to new html tag

        # if no body, append body to new soup
        # add contents of html to body

        # if both, new_soup = soup

        html_element = soup.html
        if not html_element:
            html_element = soup.new_tag("html")
            new_soup.append(html_element)
        body_element = soup.body
        if not body_element:
            body_element = soup.new_tag("body")
            new_soup.append(body_element)

        return str(new_soup)

    async def scrape_and_queue(self, downloads: list[DownloadContext]) -> None:
        xpath_locator = self.page.locator(self.xpath_selector)
        xpath_locator_count = await xpath_locator.count()

        for index in range(0, xpath_locator_count):
            try:
                html_locator = xpath_locator.nth(index)
                metadata = await self.extract_metadata(html_locator)
                html_content = await html_locator.inner_html()
                cleaned_html = self.remove_exclusions(html_content)
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
