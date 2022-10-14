from bson.json_util import dumps

from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily


class EventConvert:
    def __init__(self, document, event_type="new"):
        self.document = document
        self.event_type = event_type

    async def convert(self, target: DocDocument):
        # Since a document can have 1000+ tags, exclude all tags.
        # Otherwise, payload to big.
        # TODO: Once event model api defined,
        # refactor into DocumentEvent model which matches api definition.

        legacy_relevance = []
        if target.locations[0].document_family_id:
            document_fam = await DocumentFamily.find_one(
                {"_id": target.locations[0].document_family_id}
            )
            if document_fam:
                legacy_relevance = document_fam.legacy_relevance

        if target.document_family_id:
            document_fam = await DocumentFamily.find_one({"_id": target.document_family_id})
            if document_fam:
                legacy_relevance = document_fam.legacy_relevance

        document_load = {
            "document_id": target.id,
            "document_hash": target.checksum,
            "document_extension": target.file_extension,
            "document_legacy_relevance": legacy_relevance,
        }
        return dumps(document_load)
