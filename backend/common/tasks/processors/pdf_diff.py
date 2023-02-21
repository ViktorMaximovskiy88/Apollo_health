import asyncio
import logging

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.models.tag_comparison import TagComparison
from backend.common.services.tag_compare import TagCompare
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.storage.client import DocumentStorageClient
from backend.common.tasks.task_processor import TaskProcessor


class PDFDiffTaskProcessor(TaskProcessor):

    dependencies: list[str] = []

    def __init__(self, logger=logging) -> None:
        self.logger = logger

    async def exec(self, task: tasks.PDFDiffTask):
        doc_client = DocumentStorageClient()
        dtc = DocTextCompare(doc_client)

        (current_doc, prev_doc, tag_comparison) = await asyncio.gather(
            DocDocument.get(task.current_doc_id),
            DocDocument.get(task.prev_doc_id),
            TagComparison.find_one(
                {"current_doc_id": task.current_doc_id, "prev_doc_id": task.prev_doc_id}
            ),
        )

        tag_lineage = await TagCompare().execute(current_doc, prev_doc)
        if not tag_comparison:
            tag_comparison = await TagComparison(
                current_doc_id=current_doc.id,
                prev_doc_id=prev_doc.id,
                therapy_tag_sections=tag_lineage.therapy_tag_sections,
                indication_tag_sections=tag_lineage.indication_tag_sections,
            ).save()
        else:
            tag_comparison.therapy_tag_sections = tag_lineage.therapy_tag_sections
            tag_comparison.indication_tag_sections = tag_lineage.indication_tag_sections
            await tag_comparison.save()

        # NOTE: we may want to add this for efficiency after comparison changes have slowed
        # if not dtc.compare_exists(doc=current_doc, prev_doc=prev_doc):
        dtc.compare(doc=current_doc, prev_doc=prev_doc)

        return {
            "new_key": f"{current_doc.checksum}-{prev_doc.checksum}-new.pdf",
            "prev_key": f"{current_doc.checksum}-{prev_doc.checksum}-prev.pdf",
            "tag_comparison": tag_comparison.dict(),
        }

    async def get_progress(self) -> float:
        return 0.0
