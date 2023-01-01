import asyncio
import hashlib
import pathlib
from pathlib import Path
from typing import Any

import aiofiles

from backend.scrapeworker.file_parsers.base import FileParser


class PdfParse(FileParser):
    async def get_info(self) -> dict[str, str]:
        process = await asyncio.create_subprocess_exec(
            "pdfinfo",
            "-enc",
            "UTF-8",
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
            "-raw",
            "-q",
            "-enc",
            "UTF-8",
            self.file_path,
            "-",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdftext_out, _ = await process.communicate()
        return pdftext_out.decode("utf-8", "ignore").strip()

    async def get_md5(self, filename: str):
        async with aiofiles.open(filename, "rb") as fd:
            file_hash = hashlib.md5()
            while chunk := await fd.read(8192):
                file_hash.update(chunk)
            return file_hash.hexdigest()

    async def get_image_checksums(self):
        root_dir = Path(self.file_path).parent
        file_prefix = "image-tmp"
        process = await asyncio.create_subprocess_exec(
            "pdfimages",
            "-raw",
            "-q",
            self.file_path,
            root_dir / file_prefix,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        await process.communicate()

        checksums = set()
        for image in root_dir.glob(f"*{file_prefix}*"):
            checksum = await self.get_md5(image)
            if checksum not in checksums:
                checksums.add(checksum)

        return sorted(list(checksums))

    async def update_parsed_content(self, prev_content: dict[str, Any]) -> None:
        """Supplement previous parse with PDF parsed content"""

        new_content = await self.parse()
        prev_content["effective_date"] = new_content["effective_date"]
        prev_content["end_date"] = new_content["end_date"]
        prev_content["last_updated_date"] = new_content["last_updated_date"]
        prev_content["last_reviewed_date"] = new_content["last_reviewed_date"]
        prev_content["next_review_date"] = new_content["next_review_date"]
        prev_content["next_update_date"] = new_content["next_update_date"]
        prev_content["published_date"] = new_content["published_date"]
        prev_content["identified_dates"] = new_content["identified_dates"]

    def get_title(self, metadata):
        cont_disp_filename = None
        if self.download:
            cont_disp_filename = self.download.response.content_disposition_filename or ""
            if cont_disp_filename:
                cont_disp_filename = str(pathlib.Path(cont_disp_filename).with_suffix(""))

        title = (
            cont_disp_filename
            or metadata.get("Title")
            or metadata.get("Subject")
            or str(self.filename_no_ext)
        )
        return title
