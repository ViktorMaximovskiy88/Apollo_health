import asyncio
import logging
import threading

from backend.scrapeworker.file_parsers.base import FileParser


class PdfParse(FileParser):
    async def get_info(self) -> dict[str, str]:
        logging.info(
            f"before pdfinfo url={self.url} file_path={self.file_path} threads={threading.active_count()}"  # noqa
        )
        process = await asyncio.create_subprocess_exec(
            "pdfinfo",
            self.file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdfinfo_out, _ = await process.communicate()
        logging.info(
            f"after pdfinfo url={self.url} file_path={self.file_path} threads={threading.active_count()}"  # noqa
        )
        info = pdfinfo_out.decode("iso-8859-1", "ignore").strip()
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
        logging.info(
            f"before pdftotext url={self.url} file_path={self.file_path} threads={threading.active_count()}"  # noqa
        )
        process = await asyncio.create_subprocess_exec(
            "pdftotext",
            "-raw",
            "-q",
            "-enc",
            "Latin1",
            self.file_path,
            "-",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdftext_out, _ = await process.communicate()
        logging.info(
            f"after pdftotext url={self.url} file_path={self.file_path} threads={threading.active_count()}"  # noqa
        )
        return pdftext_out.decode("iso-8859-1", "ignore").strip()

    def get_title(self, metadata):
        title = metadata.get("Title") or metadata.get("Subject") or str(self.filename_no_ext)
        return title
