import logging
import re

import bs4

from backend.scrapeworker.file_parsers.base import FileParser


class HtmlParser(FileParser):

    # TODO ask if our text has to match the old style...
    # that SO answer was from a decade ago. BS has been updated since then..
    # docs say https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text
    async def get_text(self) -> str:
        # TODO: getting the text here causes tagging issues
        # taggers assign tags by page, but html lacks pages
        # when converted to pdf later, all tags are marked as page 1
        document_bytes = await self.read_text_file(encoding="iso-8859-1")
        self.soup = bs4.BeautifulSoup(document_bytes, features="html.parser")

        title_element = self.soup.find("title")
        self.title = title_element.string.strip() if title_element else None

        self._exclude_html()
        body_element = self.soup.find("body")
        if body_element:
            return " ".join([text for text in self.soup.find("body").stripped_strings])
        else:
            logging.error("no body tag found, why?")
            return ""

    async def get_info(self) -> dict[str, str]:
        # what does an html pages info look like?
        return {}

    def get_title(self, metadata) -> str | None:
        # metadata not used...
        return self.title

    def _exclude_html(self) -> str:

        if not self.scrape_method_config:
            return

        for selector in self.scrape_method_config.html_exclusion_selectors:
            options = {}

            if selector.attr_name:
                options["attrs"] = {}
                options["attrs"][selector.attr_name] = (
                    re.compile(rf"{selector.attr_value}", re.IGNORECASE)
                    if selector.attr_value is not None
                    else True
                )

            if selector.has_text:
                options["string"] = selector.has_text

            remove_elements = self.soup.find_all(selector.attr_element, **options)
            [element.extract() for element in remove_elements]
