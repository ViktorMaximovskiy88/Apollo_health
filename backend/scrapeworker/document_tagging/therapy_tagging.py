import asyncio
import tempfile

import spacy
from backend.common.models.doc_document import TherapyTag
from backend.common.storage.client import ModelStorageClient


class TherapyTagger():
    def __init__(self) -> None:
        self.client = ModelStorageClient()
        self.tempdir = tempfile.TemporaryDirectory()
        dirname = self.tempdir.name
        self.nlp = None
        try:
            self.client.download_directory(f'rxnorm-span/latest', dirname)
            self.nlp = spacy.load(dirname)
            # This limit assumes the default large NER model is being used
            # We are not using this model so safe to bump limit
            self.nlp.max_length = 10000000
        except:
            print(f"RxNorm Span Ruler Model not found and therefore not loaded")
    
    async def tag_document(self, full_text: str) -> list[TherapyTag]:
        if not self.nlp:
            return []

        tags: set[TherapyTag] = set()

        pages = full_text.split("\f")
        loop = asyncio.get_running_loop()
        for i, page in enumerate(pages):
            doc = await loop.run_in_executor(None, self.nlp, page)
            for span in doc.spans['sc']:
                text = span.text
                lexeme = span.vocab[span.label]
                rxnorm, display_name = lexeme.text.split('|')
                tag = TherapyTag(text=text, code=rxnorm, name=display_name, page=i)
                tags.add(tag)

        return list(tags)
