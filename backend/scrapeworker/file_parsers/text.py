from backend.scrapeworker.file_parsers.base import FileParser


# handle csv or txt
class TextParser(FileParser):
    async def get_text(self) -> str:
        text = await self.read_text_file(encoding="iso-8859-1")
        return text.strip()

    async def get_info(self) -> dict[str, str]:
        return {"title": self.filename_no_ext}

    def get_title(self, metadata) -> str | None:
        return self.filename_no_ext
