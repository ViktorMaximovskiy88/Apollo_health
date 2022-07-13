import tempfile

import spacy
from backend.common.models.doc_document import TherapyTag
from backend.common.storage.client import ModelStorageClient


class TherapyTagger():
    def __init__(self) -> None:
        self.client = ModelStorageClient()
        self.tempdir = tempfile.TemporaryDirectory()
        dirname = self.tempdir.name
        try:
            self.client.download_directory(f'rxnorm-span/latest', dirname)
            self.nlp = spacy.load(dirname)
            # This limit assumes the default large NER model is being used
            # We are not using this model so safe to bump limit
            self.nlp.max_length = 10000000
        except:
            print(f"RxNorm Span Ruler Model not found and therefore not loaded")
        
    
    async def tag_document(self, text: str) -> list[TherapyTag]:
        if not self.nlp:
            return []

        doc = self.nlp(text)
        tags: dict[str, TherapyTag] = {}
        for span in doc.spans['sc']:
            text = span.text
            lexeme = span.vocab[span.label]
            rxnorm, display_name = lexeme.text.split('|')
            tag = TherapyTag(text=text, code=rxnorm, name=display_name)
            if rxnorm not in tags:
                tags[rxnorm] = tag

        return list(tags.values())
