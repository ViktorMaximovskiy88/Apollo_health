from backend.app.utils.logger import Logger, get_diff_patch, update_and_log_diff
from backend.common.models.doc_document import DocDocument, UpdateDocDocument
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.user import User
from backend.common.services.doc_lifecycle.hooks import doc_document_save_hook, get_doc_change_info
from backend.common.services.document_analysis import upsert_for_doc_doc


class DocDocumentRepository:
    def __init__(self, logger: Logger = Logger()) -> None:
        self.logger = logger

    async def execute(self, doc: DocDocument, updates: UpdateDocDocument, current_user: User):
        updates = await self.pre_save(doc, updates)
        updated = await self.save(doc, updates, current_user)
        await self.post_save(doc, current_user)
        return updated

    async def pre_save(self, doc: DocDocument, updates: UpdateDocDocument):
        if bool(updates.__dict__):  # if updates is not empty
            updates = await self.update_user_edited_fields(doc, updates)
            self.handle_document_type_change(doc, updates)
            final_effective_date = calc_final_effective_date(updates)
            if final_effective_date:
                updates.final_effective_date = final_effective_date

        self.change_info = get_doc_change_info(updates, doc)
        return updates

    async def save(self, doc: DocDocument, updates: UpdateDocDocument, current_user: User):
        return await update_and_log_diff(self.logger, current_user, doc, updates)

    async def post_save(self, doc: DocDocument, current_user: User):
        await upsert_for_doc_doc(doc)
        original = doc.dict()
        updated = await doc_document_save_hook(doc, self.change_info)
        patch = get_diff_patch(original, updated.dict())
        filtered_patch = [obj for obj in patch if "hold_info" not in obj["path"]]
        if filtered_patch:
            await self.logger.log_change(current_user, doc, "UPDATE", filtered_patch)

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
            if (
                updates.therapy_tags
                and updates.therapy_tags[idx]
                and tag.focus != updates.therapy_tags[idx].focus
            ):
                current_user_edited_fields.append("therapy_tag_focus")
                current_user_edited_fields.append("therapy_tag")
                break

        for idx, tag in enumerate(doc.indication_tags):
            if (
                updates.indication_tags
                and updates.indication_tags[idx]
                and tag.focus != updates.indication_tags[idx].focus
            ):
                current_user_edited_fields.append("indication_tag_focus")
                current_user_edited_fields.append("indication_tag")
                break

        # editable dates
        if date_update_exists(doc.effective_date, updates.effective_date):
            current_user_edited_fields.append("effective_date")

        if date_update_exists(doc.end_date, updates.end_date):
            current_user_edited_fields.append("end_date")

        if date_update_exists(doc.last_updated_date, updates.last_updated_date):
            current_user_edited_fields.append("last_updated_date")

        if date_update_exists(doc.last_reviewed_date, updates.last_reviewed_date):
            current_user_edited_fields.append("last_reviewed_date")

        if date_update_exists(doc.next_review_date, updates.next_review_date):
            current_user_edited_fields.append("next_review_date")

        if date_update_exists(doc.next_update_date, updates.next_update_date):
            current_user_edited_fields.append("next_update_date")

        if date_update_exists(doc.published_date, updates.published_date):
            current_user_edited_fields.append("published_date")

        for field in doc.user_edited_fields:
            if field not in current_user_edited_fields:
                current_user_edited_fields.append(field)

        updates.user_edited_fields = current_user_edited_fields
        return updates


def date_update_exists(original, update):
    if not update:
        return False
    if not original:
        return True
    return original.date() != update.date()
