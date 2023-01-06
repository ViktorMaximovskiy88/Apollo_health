import logging

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import PipelineRegistry
from backend.common.models.site import Site
from backend.common.models.tasks import TaskLog
from backend.common.tasks.processors.doc_pipeline import DocPipelineTaskProcessor
from backend.common.tasks.task_processor import TaskProcessor


class SiteDocsPipelineTaskProcessor(TaskProcessor):

    dependencies: list[str] = []

    def __init__(
        self,
        logger=logging,
    ) -> None:
        self.logger = logger

    async def exec(self, task_payload: tasks.SiteDocsPipelineTask):
        stage_versions = await PipelineRegistry.fetch()
        site = await Site.get(task_payload.site_id)

        results = []
        async for doc_doc in DocDocument.find({"locations.site_id": site.id}):
            task = TaskLog(
                payload=tasks.DocPipelineTask(
                    doc_doc_id=doc_doc.id,
                    reprocess=task_payload.reprocess,
                ),
                task_type="DocPipelineTask",
                group_id=str(site.id),
            )
            task_processor: TaskProcessor = DocPipelineTaskProcessor()
            result = await task_processor.exec(
                task.payload,
                stage_versions=stage_versions,
                doc=doc_doc,
            )
            results.append({"doc_doc_id": doc_doc.id, "result": result})

        self.logger.info(f"site docs pipeline processed for site_id={site.id}")
        return len(results)

    async def get_progress(self) -> float:
        return 0.0
