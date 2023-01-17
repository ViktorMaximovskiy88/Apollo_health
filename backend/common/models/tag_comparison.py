from beanie import PydanticObjectId

from backend.common.models.base_document import BaseDocument
from backend.common.models.shared import DocumentSection


class TagComparison(BaseDocument):
    current_doc_id: PydanticObjectId
    prev_doc_id: PydanticObjectId
    therapy_tag_sections: list[DocumentSection]
    indication_tag_sections: list[DocumentSection]


class UpdateTagComparison(BaseDocument):
    current_doc_id: PydanticObjectId | None = None
    prev_doc_id: PydanticObjectId | None = None
    therapy_tag_sections: list[DocumentSection] | None = None
    indication_tag_sections: list[DocumentSection] | None = None
