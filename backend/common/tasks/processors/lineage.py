import logging

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import PipelineRegistry
from backend.common.models.site import Site
from backend.common.models.tasks import TaskLog
from backend.common.services.lineage.core import LineageService
from backend.common.tasks.processors.doc_pipeline import DocPipelineTaskProcessor
from backend.common.tasks.task_processor import TaskProcessor


class LineageTaskProcessor(TaskProcessor):

    dependencies: list[str] = []

    def __init__(
        self,
        logger=logging,
    ) -> None:
        self.logger = logger
        self.lineage_service = LineageService(logger=logger)

    async def exec(self, task_payload: tasks.SiteDocsPipelineTask):
        stage_versions = await PipelineRegistry.fetch()
        site = await Site.get(task_payload.site_id)

        all_sites_ids = [site.id]

        if task_payload.reprocess:
            site_ids = await self.lineage_service.get_shared_lineage_sites(site.id)
            all_sites_ids += site_ids

        for site_id in all_sites_ids:
            await self.lineage_service.clear_lineage_for_site(site_id)

        doc_doc_ids = []
        # make sure up-to-date
        async for doc_doc in DocDocument.find(
            {"locations.site_id": {"$in": all_sites_ids}},
        ):
            task = TaskLog(
                payload=tasks.DocPipelineTask(
                    doc_doc_id=doc_doc.id,
                    reprocess=False,
                ),
                task_type="DocPipelineTask",
                group_id=str(site.id),
            )
            task_processor: TaskProcessor = DocPipelineTaskProcessor()
            await task_processor.exec(
                task.payload,
                stage_versions=stage_versions,
                doc=doc_doc,
            )
            doc_doc_ids.append(doc_doc.id)

        for site.id in all_sites_ids:
            await self.lineage_service.process_lineage_for_doc_ids(site.id, doc_ids=doc_doc_ids)

        self.logger.info(f"lineage processed for site_id={site.id}")
        return doc_doc_ids

    async def get_progress(self) -> float:
        return 0.0
