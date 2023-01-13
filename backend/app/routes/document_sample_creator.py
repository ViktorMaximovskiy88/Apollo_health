from hashlib import md5

import fitz

from backend.common.models.translation_config import TableDetectionConfig


class DocumentSampleCreator:
    def __init__(self, config: TableDetectionConfig = TableDetectionConfig()):
        self.config = config

    def sample_hash(self):
        digest = md5(self.config.json().encode()).hexdigest()
        return digest

    def sample_file(self, filename: str = None, stream: bytes = None) -> bytes:
        reader = fitz.Document(filename=filename, stream=stream)
        writer = fitz.Document()

        start_text = self.config.start_text.lower()
        for i, page in enumerate(reader.pages()):
            page_number = i + 1

            if page_number < self.config.start_page:
                continue

            text = page.get_text().lower()
            if start_text in text:
                writer.insert_pdf(reader, from_page=i, to_page=i)
                break

        return writer.write()
