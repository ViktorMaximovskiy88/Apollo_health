from backend.app.utils.logger import Logger, update_and_log_diff
from backend.common.models.doc_document import DocDocument, UpdateDocDocument
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.user import User
from backend.common.services.doc_lifecycle.hooks import doc_document_save_hook, get_doc_change_info


class DocDocumentRepository:
    def __init__(self, logger: Logger = Logger()) -> None:
        self.logger = logger

    async def execute(self, doc: DocDocument, updates: UpdateDocDocument, current_user: User):
        updates = await self.pre_save(doc, updates)
        updated = await self.save(doc, updates, current_user)
        await self.post_save(doc)
        return updated

    async def pre_save(self, doc: DocDocument, updates: UpdateDocDocument):
        updates = await self.update_user_edited_fields(doc, updates)
        self.handle_document_type_change(doc, updates)
        final_effective_date = calc_final_effective_date(updates)
        if final_effective_date:
            updates.final_effective_date = final_effective_date
        self.change_info = get_doc_change_info(updates, doc)
        return updates

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

    async def update_user_edited_fields(self, doc: DocDocument, updates: UpdateDocDocument):
        current_user_edited_fields = []

        if updates.document_type and doc.document_type != updates.document_type:
            current_user_edited_fields.append("document_type")

        if updates.lang_code and doc.lang_code != updates.lang_code:
            current_user_edited_fields.append("lang_code")

        if updates.previous_doc_doc_id and doc.previous_doc_doc_id != updates.previous_doc_doc_id:
            current_user_edited_fields.append("previous_doc_doc_id")

        for idx, tag in enumerate(doc.therapy_tags):
            if updates.therapy_tags[idx] and tag.focus != updates.therapy_tags[idx].focus:
                current_user_edited_fields.append("therapy_tag_focus")
                break

        for idx, tag in enumerate(doc.indication_tags):
            if updates.indication_tags[idx] and tag.focus != updates.indication_tags[idx].focus:
                current_user_edited_fields.append("indication_tag_focus")
                break

        # editable dates
        if updates.effective_date and doc.effective_date.date() != updates.effective_date.date():
            current_user_edited_fields.append("effective_date")

        if updates.end_date and doc.end_date.date() != updates.end_date.date():
            current_user_edited_fields.append("end_date")

        if (
            updates.last_updated_date
            and doc.last_updated_date.date() != updates.last_updated_date.date()
        ):
            current_user_edited_fields.append("last_updated_date")

        if (
            updates.last_reviewed_date
            and doc.last_reviewed_date.date() != updates.last_reviewed_date.date()
        ):
            current_user_edited_fields.append("last_reviewed_date")

        if (
            updates.next_review_date
            and doc.next_review_date.date() != updates.next_review_date.date()
        ):
            current_user_edited_fields.append("next_review_date")

        if (
            updates.next_update_date
            and doc.next_update_date.date() != updates.next_update_date.date()
        ):
            current_user_edited_fields.append("next_update_date")

        if updates.published_date and doc.published_date.date() != updates.published_date.date():
            current_user_edited_fields.append("published_date")

        for field in doc.user_edited_fields:
            if field not in current_user_edited_fields:
                current_user_edited_fields.append(field)

        updates.user_edited_fields = current_user_edited_fields
        return updates
