import asyncio

from backend.scrapeworker.file_parsers.base import FileParser


class DocParser(FileParser):
    async def get_text(self) -> str:
        process = await asyncio.create_subprocess_exec(
            "antiword",
            self.file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        text, _ = await process.communicate()
        return text.decode("utf-8", "ignore").strip()

    async def get_info(self) -> dict[str, str]:
        return {"title": self.filename_no_ext}

    def get_title(self, metadata) -> str | None:
        return self.filename_no_ext
