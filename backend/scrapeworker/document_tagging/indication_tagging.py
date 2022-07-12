from backend.common.models.doc_document import IndicationTag
from backend.common.models.indication import Indication


class IndicationTagger():
    def __init__(self) -> None:
        self.terms: dict[str, list[Indication]] = {}

    async def terms_by_ind(self) -> dict[str, list[Indication]]:
        if self.terms:
            return self.terms
        async for indication in Indication.find():
            for term in indication.terms:
                self.terms.setdefault(term, []).append(indication)
            pass
        return self.terms

    async def tag_document(self, text: str) -> list[IndicationTag]:
        lower_text = text.lower()
        tags = []
        for term, indications in (await self.terms_by_ind()).items():
            if term.lower() in lower_text:
                for indication in indications:
                    tags.append(
                        IndicationTag(
                            text=term,
                            code=indication.indication_number
                        )
                    )
        return tags