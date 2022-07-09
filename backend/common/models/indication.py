from backend.common.models.base_document import BaseDocument

class Indication(BaseDocument):
    name: str
    terms: list[str]
    indication_number: int
    