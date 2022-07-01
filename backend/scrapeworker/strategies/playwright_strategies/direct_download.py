import logging
from functools import cached_property
from playwright.async_api import ElementHandle
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href, filter_by_hidden_value
from backend.scrapeworker.strategies import base_mixins, playwright_mixins
from backend.scrapeworker.strategies.playwright_strategies.base_strategy import (
    BaseStrategy,
)


class DirectDownloadStrategy(BaseStrategy):
    type: str = "DirectDownload"

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

    async def execute(self) -> list[Download]:
        downloads: list[Download] = []

        link_handles = await self.page.query_selector_all(self.css_selector)

        link_handle: ElementHandle
        for link_handle in link_handles:
            metadata: Metadata = await playwright_mixins.extract_metadata(link_handle)
            metadata.strategy_type = self.type

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
