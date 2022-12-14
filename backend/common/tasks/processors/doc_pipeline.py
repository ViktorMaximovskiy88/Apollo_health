import logging

import backend.common.models.tasks as tasks
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.pipeline import DocPipelineStages, PipelineRegistry
from backend.common.models.tasks import TaskLog
from backend.common.tasks.processors import task_processor_factory
from backend.common.tasks.task_processor import TaskProcessor


class DocPipelineTaskProcessor(TaskProcessor):
    def __init__(
        self,
        logger=logging,
    ) -> None:
        self.logger = logger

    async def exec(self, task: tasks.DocPipelineTask):
        stage_versions = await PipelineRegistry.fetch()

        # TODO change doc doc and rt doc IDs (related to other ticket)
        # this wont live much longer... ignore the backward naming
        rdoc = await RetrievedDocument.get(task.doc_doc_id)
        if not rdoc:
            raise Exception(f"RetrievedDocument {task.doc_doc_id} not found")

        doc = await DocDocument.find_one(DocDocument.retrieved_document_id == rdoc.id)
        if not doc:
            raise Exception(f"doc_doc {task.doc_doc_id} not found")

        if doc.classification_status == ApprovalStatus.APPROVED:
            self.logger.info(f"{doc.id} classification_status={doc.classification_status} skipping")
            return

        if not doc.pipeline_stages:
            doc.pipeline_stages = DocPipelineStages()

        pipeline = []

        # TODO get fancy later...
        # all dependencies are invalid
        if not DocPipelineStages.is_stage_valid(
            doc.pipeline_stages.content, stage_versions.content
        ):
            pipeline += [
                tasks.ContentTask(doc_doc_id=rdoc.id),
                tasks.DateTask(doc_doc_id=rdoc.id),
                tasks.DocTypeTask(doc_doc_id=rdoc.id),
                tasks.TagTask(doc_doc_id=rdoc.id),
            ]
        else:
            # check each dependency
            if not DocPipelineStages.is_stage_valid(doc.pipeline_stages.date, stage_versions.date):
                pipeline.append(tasks.DateTask(doc_doc_id=rdoc.id))

            if not DocPipelineStages.is_stage_valid(
                doc.pipeline_stages.doc_type, stage_versions.doc_type
            ):
                pipeline += [
                    tasks.DocTypeTask(doc_doc_id=rdoc.id),
                    tasks.TagTask(doc_doc_id=rdoc.id),
                ]
            elif not DocPipelineStages.is_stage_valid(doc.pipeline_stages.tag, stage_versions.tag):
                pipeline.append(tasks.TagTask(doc_doc_id=rdoc.id))

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

        # TODO some logic that updates the all_docs on site (for lineage purposes)
        # thinking... everytime doc is proccessed check then lineage?
        # what about cross site lineage?

        self.logger.info(f"pipeline processed for doc_id={doc.id}")
        return results

    async def get_progress(self) -> float:
        return 0.0
