import asyncio
from datetime import datetime, timedelta
from logging import Logger

from beanie import PydanticObjectId

from backend.app.core.settings import settings
from backend.common.core.enums import ApprovalStatus, TaskStatus
from backend.common.events.event_convert import EventConvert
from backend.common.events.send_event_client import SendEventClient
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.shared import IndicationTag, TherapyTag
from backend.common.models.site import Site


class DocLifecycleService:
    def __init__(self, logger: Logger = Logger(name="")) -> None:
        self.logger = logger

    def doc_type_needs_review(
        self, doc: DocDocument, prev_doc: DocDocument | None, site: Site | None
    ) -> bool:
        if prev_doc and doc.document_type != prev_doc.document_type:
            return True

        if site and doc.doc_type_confidence and doc.doc_type_confidence < site.doc_type_threshold:
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

    def tag_delta(self, tags: list[TherapyTag] | list[IndicationTag]):
        total = len(tags)
        if total == 0:
            return 0, 0, 0

        updated, added, removed = 0, 0, 0
        for tag in tags:
            if tag.update_status == "REMOVED":
                removed += 1
            elif tag.update_status == "UPDATED":
                updated += 1
            elif tag.update_status == "ADDED":
                added += 1
        return updated / total, added / total, removed / total

    def tags_need_review(self, doc: DocDocument) -> bool:
        tupdated, tadded, tremoved = self.tag_delta(doc.therapy_tags)
        if tupdated > 0.1 or tadded > 0.1 or tremoved > 0.1:
            return True

        iupdated, iadded, iremoved = self.tag_delta(doc.indication_tags)
        if iupdated > 0.1 or iadded > 0.1 or iremoved > 0.1:
            return True

        return False

    def extraction_delta_needs_review(self, task: ContentExtractionTask | None) -> bool:
        if not task:
            return True
        # Zero Total Delta means no Previous Version, no review needed
        if not task.delta.total:
            return False

        added_pct = task.delta.added / task.delta.total
        removed_pct = task.delta.removed / task.delta.total
        updated_pct = task.delta.updated / task.delta.total
        if added_pct > 0.10 or removed_pct > 0.05 or updated_pct > 0.10:
            return True

        return False

    def identified_dates_needs_review(self, doc: DocDocument) -> bool:
        if doc.identified_dates and len(doc.identified_dates) > 10:
            return True
        return False

    async def assess_classification_status(self, doc: DocDocument) -> tuple[ApprovalStatus, bool]:
        if doc.classification_status != ApprovalStatus.PENDING:
            return doc.classification_status, False

        prev_doc = await DocDocument.get(doc.previous_doc_doc_id or PydanticObjectId())
        site = await Site.get(doc.locations[0].site_id)

        info: list[str] = []

        if self.doc_type_needs_review(doc, prev_doc, site):
            info.append("DOC_TYPE")

        if self.effective_date_needs_review(doc, prev_doc):
            info.append("EFFECTIVE_DATE")

        if self.identified_dates_needs_review(doc):
            info.append("IDENTIFIED_DATES")

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
        info: list[str] = []
        if not doc.document_family_id:
            info.append("DOC_FAMILY")

        if any(loc for loc in doc.locations if not loc.payer_family_id):
            info.append("PAYER_FAMILY")

        if info:
            doc.family_status = ApprovalStatus.QUEUED
            doc.family_hold_info = info
            return doc.family_status, True
        elif doc.family_status == ApprovalStatus.APPROVED:
            return doc.family_status, False

        doc.family_hold_info = []
        doc.family_status = ApprovalStatus.APPROVED
        return doc.family_status, True

    async def assess_content_extraction_status(
        self, doc: DocDocument
    ) -> tuple[ApprovalStatus, bool]:
        if doc.content_extraction_status != ApprovalStatus.PENDING:
            return doc.content_extraction_status, False

        doc_family_id = doc.document_family_id or PydanticObjectId()
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

        task = await ContentExtractionTask.get(doc.content_extraction_task_id)  # type: ignore
        if task and task.status == TaskStatus.FAILED:
            doc.extraction_hold_info = ["FAILED"]
            doc.content_extraction_status = ApprovalStatus.QUEUED
            return doc.content_extraction_status, True

        if self.extraction_delta_needs_review(task):
            doc.extraction_hold_info = ["EXTRACT_DELTA"]
            doc.content_extraction_status = ApprovalStatus.QUEUED
            return doc.content_extraction_status, True

        doc.extraction_hold_info = []
        doc.content_extraction_status = ApprovalStatus.APPROVED
        return doc.content_extraction_status, True

    async def assess_intermediate_statuses(self, doc: DocDocument):
        class_status, class_edit = await self.assess_classification_status(doc)
        if class_status != ApprovalStatus.APPROVED:
            return False, class_edit

        fam_status, fam_edit = self.assess_doc_family_status(doc)
        if fam_status != ApprovalStatus.APPROVED:
            return False, class_edit or fam_edit

        extract_status, extract_edit = await self.assess_content_extraction_status(doc)
        if extract_status != ApprovalStatus.APPROVED:
            return False, class_edit or fam_edit or extract_edit

        return True, class_edit or fam_edit or extract_edit

    async def assess_document_status(self, doc: DocDocument):
        fully_approved, edit = await self.assess_intermediate_statuses(doc)
        if fully_approved:
            doc.status = ApprovalStatus.APPROVED
            if not settings.is_local:
                document_json = await EventConvert().convert(doc)
                send_event_client = SendEventClient()
                send_event_client.send_event("document-details", document_json)
        else:
            doc.status = ApprovalStatus.PENDING

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
                        "family_hold_info": doc.family_hold_info,
                    }
                },
            )

        return doc

    async def exec(self, doc_doc_ids: list[PydanticObjectId], site: Site):
        updates = []
        query = {"_id": {"$in": doc_doc_ids}, "status": {"$ne": ApprovalStatus.APPROVED}}
        async for doc in DocDocument.find(query):
            updates.append(self.assess_document_status(doc))

        asyncio.gather(*updates)
