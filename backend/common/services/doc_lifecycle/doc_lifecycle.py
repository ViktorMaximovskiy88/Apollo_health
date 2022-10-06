import pprint
from logging import Logger

from beanie import PydanticObjectId

from backend.common.models.doc_document import DocDocument


class DocLifecycleService:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.pp = pprint.PrettyPrinter(depth=4)

    def set_unlineaged_doc_state(self, doc: DocDocument):
        pass

    def set_lineaged_doc_state(self, doc: DocDocument):
        pass

    async def exec(self, doc_doc_ids: list[PydanticObjectId]):
        async for doc in DocDocument.find({"_id": {"$in": doc_doc_ids}}):
            # If classification 'pending', assess doc type confidence, tag change, effective date,
            #  lineage confidence etc.
            # If classification approved and family 'pending', check if payer family/document
            # family exists, if not, move to queued
            # If family approved and translation 'pending', check if fields allow for translation
            # and no translation, if so, send to queued
            #   If translation_id exists but not content extraction id, try to make a task
            #   If content_extraction_id exists, perform review and if lacking, more to queued
            # If everything good to go, set master approval

            # Call this function: after initial collection save, after form save, after save of
            # extraction id etc.
            if not doc.previous_doc_doc_id:
                self.set_unlineaged_doc_state(doc)
            else:
                self.set_lineaged_doc_state(doc)
