import hashlib
import re

import aiofiles

from backend.common.storage.text_extraction import TextExtractor


class DocStreamHasher:
    """Builds an md5 hash from bytes than can be passed to 'update' in chunks"""

    def __init__(self, initial: bytes | None = None):
        self.hasher = hashlib.md5()
        if initial:
            self.update(initial)

    def update(self, bytes):
        self.hasher.update(bytes)
        return self

    def hexdigest(self):
        return self.hasher.hexdigest()


def get_document_hash(extractor: TextExtractor) -> str:
    """Determine how to hash document based on mimetype."""
    mimetype = extractor.mimetype
    if mimetype == "text/html":
        doc_hash = hash_full_text(extractor.full_text)
    else:
        doc_hash = hash_bytes(document_bytes=extractor.document_bytes)
    return doc_hash


def hash_bytes(document_bytes: bytes) -> str:
    """Generate an md5 hash from bytes."""
    return DocStreamHasher(document_bytes).hexdigest()


def hash_full_text(text: str) -> str:
    """Generate a hash from a fulltext string."""
    stripped_text = re.sub(r"\s+", "", text)
    stripped_bytes = stripped_text.encode()
    return hash_bytes(document_bytes=stripped_bytes)


async def get_raw_bytes(filename: str):
    async with aiofiles.open(filename, "rb") as fd:
        return await fd.read()


async def hash_content(text: str, files: list[str] = []) -> str:
    stripped_text = re.sub(r"\s+", "", text)
    stripped_bytes = stripped_text.encode()

    hasher: DocStreamHasher = DocStreamHasher(stripped_bytes)
    for file in files:
        image_bytes = await get_raw_bytes(file)
        hasher.update(image_bytes)

    # perform cleanup here too, mreh
    for file in files:
        await aiofiles.os.remove(file)

    return hasher.hexdigest()
