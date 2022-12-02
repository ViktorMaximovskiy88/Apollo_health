from backend.app.utils.logger import Logger, update_and_log_diff
from backend.common.models.doc_document import DocDocument, UpdateDocDocument
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.user import User
from backend.common.services.doc_lifecycle.hooks import doc_document_save_hook, get_doc_change_info


class DocDocumentRepository:
    def __init__(self, logger: Logger = Logger()) -> None:
        self.logger = logger

    async def execute(self, doc: DocDocument, updates: UpdateDocDocument, current_user: User):
        await self.pre_save(doc, updates)
        updated = await self.save(doc, updates, current_user)
        await self.post_save(doc)
        return updated

    async def pre_save(self, doc: DocDocument, updates: UpdateDocDocument):
        self.handle_document_type_change(doc, updates)
        final_effective_date = calc_final_effective_date(updates)
        if final_effective_date:
            updates.final_effective_date = final_effective_date
        self.change_info = get_doc_change_info(updates, doc)

    async def save(self, doc: DocDocument, updates: UpdateDocDocument, current_user: User):
        return await update_and_log_diff(self.logger, current_user, doc, updates)

    async def post_save(self, doc: DocDocument):
        await doc_document_save_hook(doc, self.change_info)

    def handle_document_type_change(self, doc: DocDocument, updates: UpdateDocDocument):
        if (
            updates.document_type
            and updates.document_type != doc.document_type
            and (
                not updates.document_family_id
                or updates.document_family_id == doc.document_family_id
            )
        ):
            updates.document_family_id = None
