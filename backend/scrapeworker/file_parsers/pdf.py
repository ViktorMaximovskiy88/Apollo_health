import asyncio

from backend.scrapeworker.file_parsers.base import FileParser


class PdfParse(FileParser):
    async def get_info(self) -> dict[str, str]:
        process = await asyncio.create_subprocess_exec(
            "pdfinfo",
            self.file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdfinfo_out, _ = await process.communicate()
        info = pdfinfo_out.decode("utf-8", "ignore").strip()
        metadata = {}
        key = ""
        for line in info.split("\n"):
            if not line.strip():
                continue
            if ":" not in line:  # assume single value is broken into multiple lines
                value = line.strip()
                metadata[key] = f"{metadata[key]}; {value}"
                continue
            key, value = line.split(":", 1)
            value = value.strip()
            metadata[key] = value
        return metadata

    async def get_text(self):
        process = await asyncio.create_subprocess_exec(
            "pdftotext",
            self.file_path,
            "-",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdftext_out, _ = await process.communicate()
        return pdftext_out.decode("utf-8", "ignore").strip()
        
    def get_title(self, metadata):
        title = metadata.get("Title") or metadata.get("Subject") or str(self.filename_no_ext)
        return title
