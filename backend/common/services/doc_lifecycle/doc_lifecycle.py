import asyncio
from datetime import datetime, timedelta
from logging import Logger

from beanie import PydanticObjectId

from backend.common.core.enums import ApprovalStatus
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.site import Site


class DocLifecycleService:
    def __init__(self, logger: Logger = Logger(name="")) -> None:
        self.logger = logger

    def doc_type_needs_review(
        self, doc: DocDocument, prev_doc: DocDocument | None, site: Site
    ) -> bool:
        if prev_doc and doc.document_type != prev_doc.document_type:
            return True

        if doc.doc_type_confidence and doc.doc_type_confidence < site.doc_type_threshold:
            return True

        return False

    def effective_date_needs_review(self, doc: DocDocument, prev_doc: DocDocument | None) -> bool:
        if prev_doc:
            if (
                doc.final_effective_date
                and doc.final_effective_date < prev_doc.final_effective_date
            ):
                return True

        far_past = datetime.now() - timedelta(weeks=5 * 52)  # 5 years ago
        far_future = datetime.now() + timedelta(weeks=52)  # 1 year from now
        if doc.final_effective_date:
            if doc.final_effective_date > far_future:
                return True
            if doc.final_effective_date < far_past:
                return True

        return False

    def tags_need_review(self, doc: DocDocument) -> bool:
        # TODO: more than X% changes
        return False

    def extraction_delta_needs_review(self, task: ContentExtractionTask | None) -> bool:
        if not task:
            return True

        added_pct = task.delta.added / task.delta.total
        removed_pct = task.delta.removed / task.delta.total
        updated_pct = task.delta.updated / task.delta.total
        if added_pct > 0.10 or removed_pct > 0.05 or updated_pct > 0.10:
            return True

        return False

    async def assess_classification_status(
        self, doc: DocDocument, site: Site
    ) -> tuple[ApprovalStatus, bool]:
        if doc.classification_status != ApprovalStatus.PENDING:
            return doc.classification_status, False

        prev_doc = await DocDocument.get(doc.previous_doc_doc_id or PydanticObjectId())

        info: list[str] = []

        if self.doc_type_needs_review(doc, prev_doc, site):
            info.append("DOC_TYPE")

        if self.effective_date_needs_review(doc, prev_doc):
            info.append("EFFECTIVE_DATE")

        if prev_doc:
            if self.tags_need_review(doc):
                info.append("TAGS")
        else:
            info.append("LINEAGE")

        if info:
            doc.classification_hold_info = info
            doc.classification_status = ApprovalStatus.QUEUED
        else:
            doc.classification_hold_info = []
            doc.classification_status = ApprovalStatus.APPROVED

        return doc.classification_status, True

    def assess_doc_family_status(self, doc: DocDocument) -> tuple[ApprovalStatus, bool]:
        if doc.family_status not in [ApprovalStatus.PENDING, ApprovalStatus.APPROVED]:
            return doc.family_status, False

        if any(loc for loc in doc.locations if not loc.document_family_id):
            doc.family_status = ApprovalStatus.QUEUED
            return doc.family_status, True
        elif doc.family_status == ApprovalStatus.APPROVED:
            return doc.family_status, False

        doc.family_status = ApprovalStatus.APPROVED
        return doc.family_status, True

    async def assess_content_extraction_status(
        self, doc: DocDocument, site: Site
    ) -> tuple[ApprovalStatus, bool]:
        if doc.content_extraction_status != ApprovalStatus.PENDING:
            return doc.content_extraction_status, False

        location = doc.locations[0]
        doc_family_id = location.document_family_id or PydanticObjectId()
        doc_family = await DocumentFamily.get(doc_family_id)
        if not doc_family:
            raise Exception(f"Doc Family {doc_family_id} Not Found")

        if "EDITOR_AUTOMATED" not in doc_family.legacy_relevance:
            doc.content_extraction_status = ApprovalStatus.APPROVED
            return doc.content_extraction_status, True

        if doc.translation_id and not doc.content_extraction_task_id:
            return doc.content_extraction_status, False

        if not doc.translation_id:
            doc.content_extraction_status = ApprovalStatus.QUEUED
            doc.extraction_hold_info = ["NO_TRANSLATION"]
            return doc.content_extraction_status, True

        task = await ContentExtractionTask.get(doc.content_extraction_task_id or PydanticObjectId())
        if self.extraction_delta_needs_review(task):
            doc.extraction_hold_info = ["EXTRACT_DELTA"]
            doc.content_extraction_status = ApprovalStatus.QUEUED
            return doc.content_extraction_status, True

        doc.extraction_hold_info = []
        doc.content_extraction_status = ApprovalStatus.APPROVED
        return doc.content_extraction_status, True

    async def assess_intermediate_statuses(self, doc: DocDocument, site: Site):
        edit = await self.assess_classification_status(doc, site)
        if doc.classification_status != ApprovalStatus.APPROVED:
            return False, edit

        edit = self.assess_doc_family_status(doc) or edit
        if doc.family_status != ApprovalStatus.APPROVED:
            return False, edit

        edit = await self.assess_content_extraction_status(doc, site) or edit
        if doc.content_extraction_status != ApprovalStatus.APPROVED:
            return False, edit

        return True, edit

    async def assess_document_status(self, doc: DocDocument, site: Site):
        fully_approved, edit = await self.assess_intermediate_statuses(doc, site)
        if fully_approved:
            doc.status = ApprovalStatus.APPROVED

        if edit:
            await DocDocument.get_motor_collection().update_one(
                {
                    "_id": doc.id,
                },
                {
                    "$set": {
                        "status": doc.status,
                        "classification_status": doc.classification_status,
                        "classification_hold_info": doc.classification_hold_info,
                        "content_extraction_status": doc.content_extraction_status,
                        "extraction_hold_info": doc.extraction_hold_info,
                        "family_status": doc.family_status,
                    }
                },
            )

    async def exec(self, doc_doc_ids: list[PydanticObjectId], site: Site):
        updates = []
        query = {"_id": {"$in": doc_doc_ids}, "status": {"$ne": ApprovalStatus.APPROVED}}
        async for doc in DocDocument.find(query):
            updates.append(self.assess_document_status(doc, site))

        asyncio.gather(*updates)
