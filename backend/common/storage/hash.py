import hashlib
import re
from backend.common.storage.text_extraction import TextExtractor

def get_document_hash(extractor: TextExtractor) -> str:
    """ Determine how to hash document based on mimetype.
    """
    mimetype = extractor.mimetype
    if mimetype == 'text/html':
        doc_hash = hash_full_text(extractor.full_text)
    else:
        doc_hash = hash_bytes(document_bytes=extractor.document_bytes)
    return doc_hash

def hash_bytes(document_bytes: bytes) -> str:
        """ Generate an md5 hash from bytes.
        """
        hasher = hashlib.md5()
        hasher.update(document_bytes)
        return hasher.hexdigest()

def hash_full_text(html_text: str) -> str:
    """ Generate a hash from a fulltext string.
    """
    stripped_text = re.sub(r'\s+', '', html_text)
    stripped_bytes = stripped_text.encode()
    return hash_bytes(document_bytes=stripped_bytes)