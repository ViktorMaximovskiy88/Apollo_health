import logging
from functools import cached_property
from playwright.async_api import ElementHandle
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href, filter_by_hidden_value
from backend.scrapeworker.strategies import base_mixins
from backend.scrapeworker.strategies.playwright_strategies.base_strategy import (
    BaseStrategy,
)


class DirectDownloadStrategy(BaseStrategy):
    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(
            extensions=self.config.document_extensions,
            keywords=self.config.url_keywords,
        )

        hidden_value_selectors = filter_by_hidden_value(
            extensions=self.config.document_extensions,
            keywords=self.config.url_keywords,
        )

        self.selectors = self.selectors + href_selectors + hidden_value_selectors
        return ", ".join(self.selectors)

    async def collect_downloads(
        self,
        elements: list[ElementHandle],
    ) -> list[Download]:
        downloads = []

        el: ElementHandle
        for el in elements:
            metadata: Metadata = await self.extract_metadata(el)
            downloads.append(
                Download(
                    metadata=metadata,
                    request=Request(
                        url=base_mixins.join_url(
                            self.url,
                            metadata.href,
                        ),
                    ),
                )
            )

        return downloads

    async def execute(self):
        await self.nav_to_page()

        elements = await self.find_elements(self.css_selector)
        logging.info(f"elementsLength={len(elements)}")

        downloads = await self.collect_downloads(elements)
        logging.info(f"downloadsLength={len(downloads)}")

        return (elements, downloads)
