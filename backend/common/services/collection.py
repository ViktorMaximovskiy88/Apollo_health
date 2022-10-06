from ast import List
from datetime import datetime, timezone
from typing import Type
from xmlrpc.client import Boolean

import typer
from beanie.odm.operators.update.general import Set
from pydantic import BaseModel

from backend.app.utils.logger import Logger, create_and_log
from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import ManualWorkItem, SiteScrapeTask
from backend.common.models.user import User


# TODO: Define frontend error handler.
class CollectionResult(BaseModel):
    success: bool | None = True
    errors: dict | None = []  # field_name: field_value


class CollectionService:
    """
    For managing site_tasks, doc, retrieved_doc and work_items
    whenever starting, stopping or updating a collection.
    """

    def __init__(self, site: Site, current_user: User, logger: Logger) -> None:
        self.site, self.current_user, self.logger = site, current_user, logger
        self.queued_statuses: list[TaskStatus] = [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]

    # Legacy has_queued query had TaskStatus.FINISHED included in queued_statuses.
    # TODO: Ask why TaskStatus.FINISHED would be in legacy query.
    async def has_queued(self) -> Boolean:
        return self.site.last_run_status in self.queued_statuses

    async def fetch_last_queued(self) -> SiteScrapeTask:
        return await SiteScrapeTask.find_one(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            }
        )

    async def fetch_all_queued(self):
        return await SiteScrapeTask.find(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            }
        ).to_list()

    async def fetch_previous_task(self) -> SiteScrapeTask:
        return await SiteScrapeTask.find_one({"site_id": self.site.id}, sort=[("start_time", -1)])

    async def start_collecting(self) -> CollectionResult:
        """Start collecting / updating all queued tasks."""
        result: Type[CollectionResult] = CollectionResult
        err_str = f"[site: {self.site.id}] [collection_method: {self.site.collection_method}] "
        match self.site.collection_method:
            case CollectionMethod.Automated:
                result = await self.create_queued_task()
            case CollectionMethod.Manual:
                result = await self.start_manual()
            case _:
                err_str = f"Unknown collection_method: {err_str}"
                typer.secho(err_str, fg=typer.colors.RED)
                result.succuss = False
                return result
        print("start_collecting result is")
        print(result)
        # Handle site last_run finished
        # TODO: Test this code, should this let other handler set finished?
        if result and result.success:
            await self.site.update(Set({Site.last_run_status: TaskStatus.QUEUED}))
        return result

    async def stop_collecting(self) -> CollectionResult:
        """Stop collecting all queued tasks.
        Cancel each queued task, then set site.last_run_status to finished."""
        result: CollectionResult = CollectionResult
        if not self.has_queued():
            result.success = True
            return result
        match self.site.collection_method:
            case CollectionMethod.Automated:
                result: CollectionResult = await self.stop_queued_tasks()
            case CollectionMethod.Manual:
                result = await self.stop_manual()
            case _:
                # This should not happen. Cancel tasks just to be safe.
                result = await self.stop_queued_tasks()
                typer.secho(
                    f"Unknown site [{self.site.id}] collection_method "
                    "[{self.site.collection_method}]",
                    fg=typer.colors.RED,
                )
                return result
        if result.success:
            await self.site.update(Set({Site.last_run_status: TaskStatus.FINISHED}))
        return result

    async def create_queued_task(self) -> CollectionResult:
        """Create automated scrape task with queue_time of now"""
        result: CollectionResult = CollectionResult
        print("create_queued_task")
        new_scrape_task: SiteScrapeTask = SiteScrapeTask(
            site_id=self.site.id, queued_time=datetime.now(tz=timezone.utc)
        )
        scrape_task: SiteScrapeTask = await create_and_log(
            self.logger, self.current_user, new_scrape_task
        )
        if not scrape_task:
            err_msg = (
                f"Not able to create site_scrape_task for [worker_id: "
                "{new_scrape_task.worker_id} site: {self.site.id}] "
                f"collection_method: {self.site.collection_method}]"
            )
            typer.secho(err_msg, fg=typer.colors.RED)
            result.success, result.errors = False, [err_msg]
            return result
        # Set site last_run status to created task status.
        await self.site.update(
            Set(
                {
                    Site.last_run_status: scrape_task.status,
                }
            )
        )
        return result

    async def stop_queued_tasks(self) -> CollectionResult:
        """Cancel all queued site tasks."""
        print("stop_queued_tasks")
        await SiteScrapeTask.get_motor_collection().update_many(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            },
            {"$set": {"status": TaskStatus.CANCELED}},  # TODO: back to TaskStatus.CANCELING?
        )
        await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))
        return CollectionResult(success=True)

    async def start_manual(self) -> CollectionResult:
        """Start site manual collection."""
        print("start_manual")
        # await self.stop_queued_tasks()
        # return CollectionResult(success=True)

        new_task: SiteScrapeTask = SiteScrapeTask(
            site_id=self.site.id,
            initiator_id=self.current_user.id,
            start_time=datetime.now(tz=timezone.utc),
            queued_time=datetime.now(tz=timezone.utc),
            status=TaskStatus.IN_PROGRESS,
            collection_method=CollectionMethod.Manual,
        )

        # If site has a previous task, copy doc_doc, retr_doc and work_list.
        # TODO: Troubleshoot this, is this right.
        previous_task = await self.fetch_previous_task()
        if previous_task:
            new_task.documents_found = previous_task.documents_found
            new_task.retrieved_document_ids = previous_task.retrieved_document_ids
            doc_documents: List[DocDocument] = await DocDocument.find(
                {"retrieved_document_id": {"$in": new_task.retrieved_document_ids}}
            ).to_list()
            new_task.work_list = [
                ManualWorkItem(
                    document_id=f"{doc_document.id}",
                    retrieved_document_id=f"{doc_document.retrieved_document_id}",
                )
                for doc_document in doc_documents
            ]
        await create_and_log(self.logger, self.current_user, new_task)

    async def stop_manual(self) -> CollectionResult:
        """Cancel all manual tasks. Manual tasks have work_items
        which may need processed before canceling."""
        await self.stop_queued_tasks()
        last_queued_task: SiteScrapeTask = await self.fetch_last_queued()
        # Do not have queued tasks or last_queued_task
        # has not collected a document yet.
        if not last_queued_task or last_queued_task.documents_found == 0:
            return CollectionResult(success=True)

        # Unfinished manual collection with some documents already collected.
        # Cancel queued tasks and process all work actions from all queued task.
        # TODO: Loop through work_list errors and set errors in CollectionResult.
        await self.process_work_lists()
        await self.set_last_collected(last_queued_task)
        return CollectionResult(success=True)

    async def cancel_in_progress(self) -> CollectionResult:
        """Cancel only tasks which are in progress.
        Since a doc was never collected, set TaskStatus.CANCELED instead of CANCELING.
        """
        print("canceling in_progress")
        await SiteScrapeTask.get_motor_collection().update_many(
            {"site_id": self.site.id, "status": {"$in": [TaskStatus.IN_PROGRESS]}},
            {"$set": {"status": TaskStatus.CANCELED}},
        )
        await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))
        return CollectionResult(success=True)

    async def set_last_collected(self, task) -> CollectionResult:
        """Update last_collected_date for retrieved_docs and retrieved_doc's doc."""
        print("setting retrieved_docs")
        retrieved_documents: list[RetrievedDocument] = (
            await RetrievedDocument.find_many({"_id": {"$in": task.retrieved_document_ids}})
            .sort("-first_collected_date")
            .to_list()
        )
        if not retrieved_documents:
            self.logger.info(f"No retrieved_docs for site_scrape_task[{task.id}]")
            return CollectionResult(success=True)

        for r_doc in retrieved_documents:
            print("set_retrieved_docs")
            if datetime.date(r_doc.last_collected_date) < datetime.today().date():
                print("setting_last_collected")
                await RetrievedDocument.get_motor_collection().find_one_and_update(
                    {"_id": r_doc.id},
                    {"$set": {"last_collected_date": datetime.now(tz=datetime.timezone.utc)}},
                )
                await DocDocument.get_motor_collection().find_one_and_update(
                    {"retrieved_document_id": r_doc.id},
                    {"$set": {"last_collected_date": datetime.now(tz=datetime.timezone.utc)}},
                )
        return CollectionResult(success=True)

    async def process_work_lists(self) -> CollectionResult:
        """
        Go through every queued task's work_list and process each action.
        Set state for site, scrape_tasks, work_items, doc_doc and retr_doc.
        """
        print("processing work_list")
        work_list_result: Type[CollectionResult] = CollectionResult
        print("work_list_result1")

        queued_site_tasks: List[SiteScrapeTask] = await self.fetch_all_queued()
        for queued_site_task in queued_site_tasks:
            for work_item in queued_site_task.work_list:
                work_item_result: CollectionResult = await self.process_work_item(
                    target_task=queued_site_task, work_item=work_item
                )
                if work_item_result and work_item_result.success is False:
                    print("got errors")
                    print("work_item_error")
                    print(work_item_result)
                    work_list_result.success = False
                    # TODO: What happens on work item error.
                    # TODO: Filter an update existing error.
                    work_list_result.errors.append(work_item_result)
        print(work_list_result)
        print("work_list_result2")
        if work_list_result and work_list_result.success is False:
            print("!!!! work_list_errors !!!!")
            print(work_list_result)

        return work_list_result

    async def process_work_item(
        self, target_task: SiteScrapeTask, work_item: ManualWorkItem
    ) -> CollectionResult:
        """
        TODO: go through each work_list item, set finished or failed.
        set associations depending on work_list item action.
        """
        print("processing work_item")
        print(work_item)
        work_item_header_msg = (
            f"work_item selected: [{work_item.selected}] doc_id: [{work_item.document_id}] "
            f"retrieved_document_id: [{work_item.retrieved_document_id}] not found."
        )
        print("error_header is ")
        print(work_item_header_msg)
        match work_item.selected:
            case "NOT_FOUND":
                typer.secho(
                    f"NOT_FOUND {work_item_header_msg}",
                    fg=typer.colors.BRIGHT_GREEN,
                )
            case "FOUND":
                typer.secho(
                    f"FOUND {work_item_header_msg}",
                    fg=typer.colors.BRIGHT_GREEN,
                )
            case _:
                typer.secho(
                    f"OTHER {work_item_header_msg}",
                    fg=typer.colors.BRIGHT_GREEN,
                )
        return CollectionResult(success=True)
        # NOT_FOUND
        # Remove retrieved_document from target_test.retrieved_documents.
        # set_retrieved_docs = [
        #     PydanticObjectId(retrieved_document.id),
        #     for retrieved_document in target_task.retrieved_document_ids
        #     if PydanticObjectId(retrieved_document) != work_item.retrieved_document_id
        # ]

        # FOUND
        # Update last_collected_date for doc and retrieved_doc.
        # doc = await DocDocument.get_motor_collection().find_one_and_update(
        #     {"retrieved_document_id": updates.retrieved_document_id},
        #     {"$set": {"last_collected_date": datetime.now(tz=timezone.utc)}},
        # )
        # retrieved_doc = await RetrievedDocument.get_motor_collection().find_one_and_update(
        #     {"_id": updates.retrieved_document_id},
        #     {"$set": {"last_collected_date": datetime.now(tz=timezone.utc)}},
        # )
