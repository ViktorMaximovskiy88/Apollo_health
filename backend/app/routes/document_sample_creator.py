from hashlib import md5
from io import BufferedReader, BytesIO

from PyPDF2 import PdfReader, PdfWriter

from backend.common.models.translation_config import TableDetectionConfig


class DocumentSampleCreator:
    def __init__(self, config: TableDetectionConfig = TableDetectionConfig()):
        self.config = config

    def sample_hash(self):
        digest = md5(self.config.json().encode()).hexdigest()
        return digest

    def sample_file(self, file: BufferedReader) -> BytesIO:
        reader = PdfReader(file)

        writer = PdfWriter()

        start_text = self.config.start_text.lower()
        for i, page in enumerate(reader.pages):
            page_number = i + 1

            if page_number < self.config.start_page:
                continue

            text = page.extract_text().lower()
            if start_text in text:
                writer.add_page(page)
                break

        stream = BytesIO()
        writer.write(stream)
        stream.seek(0)

        return stream
