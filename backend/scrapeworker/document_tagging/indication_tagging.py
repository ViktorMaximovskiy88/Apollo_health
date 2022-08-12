import asyncio

import spacy
from spacy.tokens import Span

from backend.common.models.doc_document import IndicationTag
from backend.common.models.indication import Indication


class IndicationTagger:
    def __init__(self) -> None:
        self.terms: dict[str, list[Indication]] = {}
        self.nlp = None
        self.lock = asyncio.Lock()

    async def model(self):
        if not self.nlp:
            async with self.lock:
                self.nlp = spacy.blank("en")
                # saw a value of 20074378... bumping more
                self.nlp.max_length = 30000000
                ruler = self.nlp.add_pipe(
                    "span_ruler", config={"spans_key": "sc", "phrase_matcher_attr": "LOWER"}
                )
                async for indication in Indication.find():
                    for term in indication.terms:
                        ruler.add_patterns(
                            [
                                {  # type: ignore
                                    "label": f"{term}|{indication.indication_number}",
                                    "pattern": term,
                                }
                            ]
                        )
        return self.nlp

    async def tag_document(self, text: str) -> list[IndicationTag]:
        nlp = await self.model()
        if not nlp:
            return []

        tags = set()
        pages = text.split("\f")
        loop = asyncio.get_running_loop()
        for i, page in enumerate(pages):
            doc = await loop.run_in_executor(None, nlp, page)
            spans: list[Span] = doc.spans.get("sc", [])
            for span in spans:
                text = span.text
                lexeme = span.vocab[span.label]
                term, indication_number = lexeme.text.split("|")
                tags.add(
                    IndicationTag(
                        text=term,
                        page=i,
                        code=int(indication_number),
                    )
                )
        return list(tags)
