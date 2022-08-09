import logging

import bs4

from backend.scrapeworker.file_parsers.base import FileParser


class HtmlParser(FileParser):
    # TODO ask if our text has to match the old style...
    # that SO answer was from a decade ago. BS has been updated since then..
    # docs say https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text
    async def get_text(self) -> str:
        document_bytes = await self.get_bytes()
        soup = bs4.BeautifulSoup(document_bytes, features="html.parser")

        title_element = soup.find("title")
        self.title = title_element.string.strip() if title_element else None

        body_element = soup.find("body")
        if body_element:
            return " ".join([text for text in soup.find("body").stripped_strings])
        else:
            logging.error("no body tag found, why?")
            return ""

    async def get_info(self) -> dict[str, str]:
        # what does an html pages info look like?
        return {}

    def get_title(self, metadata) -> str | None:
        # metadata not used...
        return self.title
