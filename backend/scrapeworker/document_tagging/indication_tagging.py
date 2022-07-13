import re
from typing import Pattern
from backend.common.models.doc_document import IndicationTag
from backend.common.models.indication import Indication


class IndicationTagger():
    def __init__(self) -> None:
        self.terms: dict[str, list[Indication]] = {}
        self.terms_regex: Pattern[str] | None = None

    async def terms_by_ind(self) -> dict[str, list[Indication]]:
        if not self.terms:
            async for indication in Indication.find():
                for term in indication.terms:
                    self.terms.setdefault(term, []).append(indication)
                pass
        return self.terms
    
    async def get_terms_regex(self) -> Pattern[str]:
        if not self.terms_regex:
            rgx_list = []
            for term in await self.terms_by_ind():
                rgx_list.append(f"(\\b{term}\\b)")
            rgx = re.compile('|'.join(rgx_list), re.IGNORECASE)
            self.terms_regex = rgx

        return self.terms_regex

    async def tag_document(self, text: str) -> list[IndicationTag]:
        tags = []
        if match := (await self.get_terms_regex()).search(text):
            groups = match.groups()
            for i, indications in enumerate((await self.terms_by_ind()).values()):
                found = groups[i]
                if not found:
                    continue 

                for indication in indications:
                    tags.append(
                        IndicationTag(
                            text=found,
                            code=indication.indication_number
                        )
                    )
        return tags
