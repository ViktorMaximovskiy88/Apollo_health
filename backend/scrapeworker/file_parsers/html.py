import bs4

from backend.scrapeworker.file_parsers.base import FileParser


class HtmlParser(FileParser):
    # TODO ask if our text has to match the old style...
    # that SO answer was from a decade ago. BS has been updated since then..
    # docs say https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text
    async def get_text(self) -> str:
        document_bytes = await self.get_bytes()
        soup = bs4.BeautifulSoup(document_bytes, features="html.parser")
        # hack for now...
        self.title = soup.find("title").string
        return " ".join([text for text in soup.find("body").stripped_strings])

    async def get_info(self) -> dict[str, str]:
        # what does an html pages info look like?
        return {}

    def get_title(self, metadata) -> str | None:
        # metadata not used...
        return self.title
