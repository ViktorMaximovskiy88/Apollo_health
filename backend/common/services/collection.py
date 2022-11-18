from ast import List
from datetime import datetime, timezone
from typing import Type, Union
from xmlrpc.client import Boolean

import typer
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pyparsing import Optional

from backend.app.utils.logger import Logger, create_and_log
from backend.common.core.config import env_type
from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_mixins import find_site_index
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import ManualWorkItem, SiteScrapeTask, WorkItemOption
from backend.common.models.user import User


class CollectionResponse(BaseModel):
    success: Boolean | None = True
    errors: list | None = []
    nav_id: PydanticObjectId | None = None

    def add_error(self, error: str) -> None:
        typer.secho(error, fg=typer.colors.RED)
        self.success = False
        self.errors.append(error)

    # Send http status code and object that matches isErrorWithData.
    def raise_error(self, status: status = status.HTTP_409_CONFLICT) -> Optional:
        raise HTTPException(status, jsonable_encoder("\n".join(self.errors)))


class CollectionService:
    """
    For managing site_tasks, doc, retrieved_doc and work_items
    whenever starting, stopping or updating a collection.
    """

    queued_statuses: list[TaskStatus] = [
        TaskStatus.QUEUED,
        TaskStatus.PENDING,
        TaskStatus.IN_PROGRESS,
    ]

    def __init__(self, site: Site, current_user: User, logger: Logger) -> None:
        self.site: Site = site
        self.current_user: User = current_user
        self.logger: Logger = logger
        self.found_docs_total = 0
        self.last_queued: SiteScrapeTask | None = None

    async def has_queued(self) -> SiteScrapeTask | Boolean:
        if self.last_queued:
            return self.last_queued
        last_queued_task: SiteScrapeTask = await self.fetch_last_queued()
        if last_queued_task:
            self.last_queued: SiteScrapeTask = last_queued_task
            return last_queued_task
        return False

    async def fetch_last_queued(self) -> SiteScrapeTask:
        return await SiteScrapeTask.find_one(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            },
            sort=[("start_time", -1)],
        )

    async def fetch_all_queued(self) -> Union[SiteScrapeTask, Boolean]:
        if not await self.has_queued():
            return False
        return await SiteScrapeTask.find(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            }
        ).to_list()

    async def fetch_previous_task(self) -> SiteScrapeTask:
        return await SiteScrapeTask.find_one({"site_id": self.site.id}, sort=[("start_time", -1)])

    async def start_collecting(self) -> CollectionResponse:
        """Create site scrape task using site config."""
        result: CollectionResponse = CollectionResponse()
        last_run_status = TaskStatus.QUEUED
        match self.site.collection_method:
            case CollectionMethod.Automated:
                result = await self.start_automated_task()
            case CollectionMethod.Manual:
                result = await self.start_manual_task()
                last_run_status = TaskStatus.IN_PROGRESS
            case _:
                result.add_error(f"Collection Method Invalid: {self.site.collection_method}")
                return result
        if not result.errors:
            await self.site.update(
                Set(
                    {
                        Site.last_run_status: last_run_status,
                        Site.last_run_time: datetime.now(tz=timezone.utc),
                    }
                )
            )
        return result

    async def stop_collecting(self) -> CollectionResponse:
        """
        Stop collecting all queued or running tasks.
        """
        result = CollectionResponse()

        match self.site.collection_method:
            case CollectionMethod.Automated:
                result: CollectionResponse = await self.stop_all_tasks()
            case CollectionMethod.Manual:
                result: CollectionResponse = await self.stop_manual_task()
            case _:
                # This should not happen. Cancel tasks just to be safe.
                result: CollectionResponse = await self.stop_all_tasks()
                typer.secho(
                    f"Unknown site [{self.site.id}] collection_method "
                    f"[{self.site.collection_method}]",
                    fg=typer.colors.RED,
                )
                return result

        if not result.errors:
            last_queued_task: SiteScrapeTask = await self.fetch_previous_task()
            await self.site.update(
                Set(
                    {
                        Site.last_run_status: TaskStatus.FINISHED,
                        Site.last_run_documents: len(last_queued_task.retrieved_document_ids),
                    }
                )
            )
        return result

    async def start_automated_task(self) -> CollectionResponse:
        """Create automated scrape task with queue_time of now"""
        response: CollectionResponse = CollectionResponse()
        await self.stop_all_tasks()
        new_scrape_task: SiteScrapeTask = SiteScrapeTask(
            site_id=self.site.id,
            queued_time=datetime.now(tz=timezone.utc),
            documents_found=0,  # Incremented during automated scrape.
        )
        scrape_task: SiteScrapeTask = await create_and_log(
            self.logger, self.current_user, new_scrape_task
        )
        if not scrape_task:
            response.add_error(
                f"Not able to create site_scrape_task for worker_id"
                f"[{new_scrape_task.worker_id}] site[{self.site.id}]"
            )
            return response

        # Set nav_id as task id to (optionally) navigate to after success.
        response.nav_id = scrape_task.id
        return response

    async def start_manual_task(self) -> CollectionResponse:
        """Start site manual collection."""
        response: CollectionResponse = CollectionResponse()
        await self.stop_all_tasks()
        now: datetime = datetime.now(tz=timezone.utc)

        # Create a new in_progress manual task and set queued to now.
        new_task: SiteScrapeTask = SiteScrapeTask(
            site_id=self.site.id,
            initiator_id=self.current_user.id,
            start_time=now,
            queued_time=now,
            last_active=now,
            status=TaskStatus.IN_PROGRESS,
            collection_method=CollectionMethod.Manual,
        )
        # If previous task, add previous task's docs to this task's work_list
        # with a default work_item selection of unhandled.
        previous_task: SiteScrapeTask = await self.fetch_previous_task()
        if previous_task:
            new_task.documents_found = previous_task.documents_found
            doc_docs: List[DocDocument] = await DocDocument.find(
                {"retrieved_document_id": {"$in": previous_task.retrieved_document_ids}}
            ).to_list()
            for doc_doc in doc_docs:
                new_task.retrieved_document_ids.append(f"{doc_doc.retrieved_document_id}")
                new_task.work_list.append(
                    ManualWorkItem(
                        document_id=f"{doc_doc.id}",
                        retrieved_document_id=f"{doc_doc.retrieved_document_id}",
                    )
                )

        # Create new manual task and respond with nav link.
        created_task: SiteScrapeTask = await create_and_log(
            self.logger, self.current_user, new_task
        )
        if not created_task:
            response.add_error("Unable to create new scrape task.")
        else:
            response.nav_id = created_task.id
        return response

    async def stop_manual_task(self) -> CollectionResponse:
        """
        Cancel running manual task. If any pending work_items, raise error
        """
        response: CollectionResponse = CollectionResponse()

        # Make sure there is a queued task with no unfinished work_items.
        last_queued_task: SiteScrapeTask = await self.fetch_last_queued()
        if not last_queued_task:
            return response
        for work_item in last_queued_task.work_list:
            if work_item.selected == WorkItemOption.UNHANDLED:
                retr_doc: RetrievedDocument | None = await RetrievedDocument.find_one(
                    {"_id": work_item.retrieved_document_id},
                )
                response.success = False
                response.add_error(f"{retr_doc.name}")
        if not response.success:
            response.raise_error()

        # Process all work actions from current manual collection task.
        response = await self.process_work_lists()
        if not response.success:
            response.raise_error()
        await self.stop_all_tasks()

        return response

    async def cancel_in_progress(self) -> None:
        """
        Cancel only tasks which are in progress.
        Since a doc was never collected, set TaskStatus.CANCELED instead of CANCELING.
        """
        await SiteScrapeTask.get_motor_collection().update_many(
            {"site_id": self.site.id, "status": {"$in": [TaskStatus.IN_PROGRESS]}},
            {"$set": {"status": TaskStatus.CANCELED}},
        )
        await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))

    async def stop_all_tasks(self) -> Boolean:
        """Stop all queued or running site tasks."""
        err = await SiteScrapeTask.get_motor_collection().update_many(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            },
            {"$set": {"status": TaskStatus.FINISHED}},
        )
        if not err:
            await self.site.update(Set({Site.last_run_status: TaskStatus.FINISHED}))
            return CollectionResponse(success=True)
        else:
            return CollectionResponse(success=False)

    async def set_all_last_collected(self, task) -> CollectionResponse:
        """Update all task retrieved_docs and doc_docs last_collected_date."""
        response: CollectionResponse = CollectionResponse()
        now: datetime = datetime.now(tz=timezone.utc)
        retrieved_documents: list[RetrievedDocument] = (
            await RetrievedDocument.find_many({"_id": {"$in": task["retrieved_document_ids"]}})
            .sort("-first_collected_date")
            .to_list()
        )
        if not retrieved_documents:
            response.add_error(
                f"set_last_collected: No retrieved_docs for site_scrape_task[{task.id}]"
            )
            return response

        for r_doc in retrieved_documents:
            if datetime.date(r_doc.last_collected_date) < datetime.today().date():
                await RetrievedDocument.get_motor_collection().find_one_and_update(
                    {"_id": r_doc.id},
                    {"$set": {"last_collected_date": now}},
                )
                await DocDocument.get_motor_collection().find_one_and_update(
                    {"retrieved_document_id": r_doc.id},
                    {"$set": {"last_collected_date": now}},
                )
        return response

    async def set_first_collected(self, doc) -> CollectionResponse:
        """Update all task retrieved_docs and doc_docs first_collected_date."""
        now: datetime = datetime.now(tz=timezone.utc)
        retr_doc: RetrievedDocument | None = await RetrievedDocument.find_one(
            {"_id": doc.id},
        )
        if not retr_doc.first_collected_date:
            retr_doc.first_collected_date = now
        if retr_doc.locations:
            site_loc_index: int = find_site_index(retr_doc, self.site.id)
            if not retr_doc.locations[site_loc_index].first_collected_date:
                retr_doc.locations[site_loc_index].first_collected_date = now
        await retr_doc.save()
        doc_doc: DocDocument | None = await DocDocument.find_one(
            {"retrieved_document_id": retr_doc.id},
        )
        if not doc_doc.first_collected_date:
            doc_doc.first_collected_date = now
        if doc_doc.locations:
            site_loc_index: int = find_site_index(doc_doc, self.site.id)
            if not doc_doc.locations[site_loc_index].first_collected_date:
                doc_doc.locations[site_loc_index].first_collected_date = now
        await doc_doc.save()
        return CollectionResponse(success=True)

    async def set_last_collected(self, doc) -> CollectionResponse:
        """
        Update all task retrieved_docs and doc_docs last_collected_date.
        """
        now: datetime = datetime.now(tz=timezone.utc)
        retr_doc: RetrievedDocument | None = await RetrievedDocument.find_one(
            {"_id": doc.id},
        )
        retr_doc.last_collected_date = now
        if retr_doc.locations:
            site_loc_index: int = find_site_index(retr_doc, self.site.id)
            retr_doc.locations[site_loc_index].last_collected_date = now
        await retr_doc.save()
        doc_doc: DocDocument | None = await DocDocument.find_one(
            {"retrieved_document_id": retr_doc.id},
        )
        doc_doc.last_collected_date = now
        if doc_doc.locations:
            site_loc_index: int = find_site_index(doc_doc, self.site.id)
            doc_doc.locations[site_loc_index].last_collected_date = now
        await doc_doc.save()
        return CollectionResponse(success=True)

    async def set_task_complete(self, task) -> CollectionResponse:
        """
        Set sitescrapetask completed dates and statuses.
        """
        now: datetime = datetime.now(tz=timezone.utc)
        task.end_time = now
        task.last_doc_collected = now
        await task.save()
        return CollectionResponse(success=True)

    async def process_work_lists(self) -> CollectionResponse:
        """
        Go through every queued task's work_list and process each action.
        Set state for site, scrape_tasks, work_items, doc_doc and retr_doc.
        """
        work_list_response: Type[CollectionResponse] = CollectionResponse()
        queued_site_tasks: List[SiteScrapeTask] = await self.fetch_all_queued()

        for queued_site_task in queued_site_tasks:
            for item_index, work_item in enumerate(queued_site_task.work_list):
                work_item_response: CollectionResponse = await self.process_work_item(
                    target_task=queued_site_task,
                    work_item=work_item,
                    item_index=item_index,
                )
                if work_item_response.errors:
                    work_list_response.add_error(work_item_response.errors[0])
            queued_site_task.documents_found = self.found_docs_total
            await self.set_task_complete(queued_site_task)
            await queued_site_task.save()

        return work_list_response

    async def process_work_item(
        self,
        target_task: SiteScrapeTask,
        work_item: ManualWorkItem,
        item_index: int,
    ) -> CollectionResponse:
        """Process a site_scrape_task work_item action"""
        result: CollectionResponse = CollectionResponse()
        work_item.is_new = False
        work_item.action_datetime = datetime.now(tz=timezone.utc)
        target_task.work_list[item_index] = work_item
        retr_doc: RetrievedDocument | None = await RetrievedDocument.find_one(
            {"_id": work_item.retrieved_document_id},
        )
        if env_type == "local" and work_item.selected != WorkItemOption.UNHANDLED:
            work_item_msg: str = (
                f"work_item selected[{work_item.selected}] in task[{target_task.id}] "
                f"doc_id[{work_item.document_id}] "
                f"retrieved_document_id[{work_item.retrieved_document_id}]"
            )
            typer.secho(work_item_msg, fg=typer.colors.BRIGHT_GREEN)

        match work_item.selected:
            case WorkItemOption.FOUND:
                await self.set_last_collected(retr_doc)
                self.found_docs_total += 1
            case WorkItemOption.NEW_DOCUMENT:
                await self.set_first_collected(retr_doc)
                await self.set_last_collected(retr_doc)
                self.found_docs_total += 1
            case WorkItemOption.NEW_VERSION:
                await self.set_first_collected(retr_doc)
                await self.set_last_collected(retr_doc)
                self.found_docs_total += 1
            case WorkItemOption.NOT_FOUND:
                target_task.retrieved_document_ids = [
                    f"{retr_id}"
                    for retr_id in target_task.retrieved_document_ids
                    if f"{retr_id}" != f"{work_item.retrieved_document_id}"
                ]
            case WorkItemOption.UNHANDLED:
                result.add_error(f"{retr_doc.name}")
                return result

        return result


def find_work_item_index(doc, task, raise_exception=False, err_msg="") -> int:
    if not err_msg:
        err_msg = f"ERROR: Not able to find doc.id in work list for task[{task.id}]"
    # Is doc_doc.
    if hasattr(doc, "retrieved_document_id"):
        work_item_index: int = next(
            (i for i, item in enumerate(task.work_list) if f"{item.document_id}" == f"{doc.id}"),
            -1,
        )
    # Is retr_doc.
    else:
        work_item_index: int = next(
            (
                i
                for i, item in enumerate(task.work_list)
                if f"{item.retrieved_document_id}" == f"{doc.id}"
            ),
            -1,
        )
    if work_item_index == -1 and raise_exception:
        typer.secho(err_msg, fg=typer.colors.RED)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            err_msg,
        )
    return work_item_index
