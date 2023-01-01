import logging

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry
from backend.common.models.tasks import TaskLog
from backend.common.tasks.processors import task_processor_factory
from backend.common.tasks.task_processor import TaskProcessor


class DocPipelineTaskProcessor(TaskProcessor):

    dependencies: list[str] = []

    def __init__(
        self,
        logger=logging,
    ) -> None:
        self.logger = logger

    async def exec(
        self,
        task: tasks.DocPipelineTask,
        stage_versions: PipelineRegistry | None = None,
        doc: DocDocument | None = None,
    ):
        if not stage_versions:
            stage_versions = await PipelineRegistry.fetch()

        if not doc:
            doc = await DocDocument.get(task.doc_doc_id)

        if not doc.pipeline_stages:
            doc.pipeline_stages = DocPipelineStages()

        pipeline = []
        # TODO get fancy later...
        # all dependencies are invalid
        if task.reprocess or not DocPipelineStages.is_stage_valid(
            doc.pipeline_stages.content, stage_versions.content
        ):
            pipeline += [
                tasks.ContentTask(doc_doc_id=doc.id, reprocess=task.reprocess),
                tasks.DateTask(doc_doc_id=doc.id, reprocess=task.reprocess),
                tasks.DocTypeTask(doc_doc_id=doc.id, reprocess=task.reprocess),
                tasks.TagTask(doc_doc_id=doc.id, reprocess=task.reprocess),
            ]
        else:
            # check each dependency
            if not DocPipelineStages.is_stage_valid(doc.pipeline_stages.date, stage_versions.date):
                pipeline.append(tasks.DateTask(doc_doc_id=doc.id))

            if not DocPipelineStages.is_stage_valid(
                doc.pipeline_stages.doc_type, stage_versions.doc_type
            ):
                pipeline += [
                    tasks.DocTypeTask(doc_doc_id=doc.id),
                    tasks.TagTask(doc_doc_id=doc.id),
                ]
            elif not DocPipelineStages.is_stage_valid(doc.pipeline_stages.tag, stage_versions.tag):
                pipeline.append(tasks.TagTask(doc_doc_id=doc.id))

        results = []
        for task_payload in pipeline:
            task_type = type(task_payload).__name__
            task = TaskLog(
                payload=task_payload,
                task_type=task_type,
                group_id="",
            )
            task_processor: TaskProcessor = task_processor_factory(task)
            result = await task_processor.exec(task.payload)
            results.append(result)

        self.logger.info(f"pipeline processed for doc_id={doc.id}")
        return results

    async def get_progress(self) -> float:
        return 0.0
