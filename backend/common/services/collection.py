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
from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import ManualWorkItem, SiteScrapeTask
from backend.common.models.user import User


class CollectionResponse(BaseModel):
    has_error: Boolean | None = False
    errors: list | None = []
    nav_id: PydanticObjectId | None = None

    def add_error(self, error: str) -> None:
        typer.secho(error, fg=typer.colors.RED)
        self.has_error = True
        self.errors.append(error)

    # Send http status code and object that matches isErrorWithData.
    def raise_error(self, status: status = status.HTTP_406_NOT_ACCEPTABLE) -> Optional:
        raise HTTPException(status, jsonable_encoder(self.errors))


class CollectionService:
    """
    For managing site_tasks, doc, retrieved_doc and work_items
    whenever starting, stopping or updating a collection.
    """

    def __init__(self, site: Site, current_user: User, logger: Logger) -> None:
        self.site, self.current_user, self.logger = site, current_user, logger
        self.queued_statuses: list[TaskStatus] = [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]
        self.last_queued = None

    # TODO: Ask why TaskStatus.FINISHED would be in legacy query.
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
            }
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
        """Start collecting / updating all queued tasks."""
        result = CollectionResponse()
        err_str = f"[site: {self.site.id}] [collection_method: {self.site.collection_method}] "
        match self.site.collection_method:
            case CollectionMethod.Automated:
                result = await self.create_queued_task()
            case CollectionMethod.Manual:
                result = await self.start_manual()
            case _:
                err_str: str = f"Unknown collection_method: {err_str}"
                result.add_error(err_str)
                return result
        if not result.errors:
            await self.site.update(Set({Site.last_run_status: TaskStatus.QUEUED}))
        print("start_collecting result is")
        print(result)
        return result

    async def stop_collecting(self) -> CollectionResponse:
        """Stop collecting all queued tasks.
        Cancel each queued task, then set site.last_run_status to finished."""
        result = CollectionResponse()
        print("stopping collecting")
        if not await self.has_queued():
            print("cannot stop, no queued")
            return result
        match self.site.collection_method:
            case CollectionMethod.Automated:
                result: CollectionResponse = await self.stop_queued_tasks()
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
        if not result.errors:
            print("setting site to finished")
            await self.site.update(Set({Site.last_run_status: TaskStatus.FINISHED}))
        else:
            print("haz error")
            print(result)
        return result

    async def create_queued_task(self) -> CollectionResponse:
        """Create automated scrape task with queue_time of now"""
        await self.stop_queued_tasks()
        result = CollectionResponse()
        new_scrape_task: SiteScrapeTask = SiteScrapeTask(
            site_id=self.site.id, queued_time=datetime.now(tz=timezone.utc)
        )
        scrape_task: SiteScrapeTask = await create_and_log(
            self.logger, self.current_user, new_scrape_task
        )
        if not scrape_task:
            err_msg: str = (
                f"Not able to create site_scrape_task for [worker_id: "
                "{new_scrape_task.worker_id} site: {self.site.id}] "
                f"collection_method: {self.site.collection_method}]"
            )
            result.add_error(err_msg)
            return result

        # Set site last_run status to created task status.
        # and id to navigate to newly created site_task_id.
        result.nav_id = scrape_task.id
        await self.site.update(
            Set(
                {
                    Site.last_run_status: scrape_task.status,
                }
            )
        )
        return result

    async def stop_queued_tasks(self) -> Boolean:
        """Cancel all queued site tasks."""
        print("stop_queued_tasks")
        err = await SiteScrapeTask.get_motor_collection().update_many(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            },
            {"$set": {"status": TaskStatus.CANCELED}},  # TODO: back to TaskStatus.CANCELING?
        )
        if not err:
            await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))
            return True
        else:
            return False

    async def start_manual(self) -> CollectionResponse:
        """Start site manual collection."""
        response = CollectionResponse()
        print("start_manual")
        await self.stop_queued_tasks()

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
        previous_task: SiteScrapeTask = await self.fetch_previous_task()
        if previous_task:
            print("HAS PREVIOUS")
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
        created_task: SiteScrapeTask = await create_and_log(
            self.logger, self.current_user, new_task
        )
        if not created_task:
            print(created_task)
            print("error creating task")
            response.add_error(created_task.error_message)
        else:
            response.nav_id = created_task.id
        print("stopping manual")
        print(response)

        return response

    async def stop_manual(self) -> CollectionResponse:
        """Cancel all manual tasks. Manual tasks have work_items
        which may need processed before canceling."""
        response: CollectionResponse = CollectionResponse()
        last_queued_task: SiteScrapeTask = await self.fetch_last_queued()
        # Do not have queued tasks or
        # last_queued_task has not collected a document yet.
        if not last_queued_task or last_queued_task.documents_found == 0:
            return CollectionResponse(errors=[])

        # Unfinished manual collection with some documents already collected.
        # Cancel queued tasks and process all work actions from all queued task.
        # TODO: Loop through work_list errors and set errors in CollectionResponse.
        response = await self.process_work_lists()
        await self.stop_queued_tasks()
        await self.set_last_collected(last_queued_task)
        return response

    async def cancel_in_progress(self) -> None:
        """Cancel only tasks which are in progress.
        Since a doc was never collected, set TaskStatus.CANCELED instead of CANCELING.
        """
        print("canceling in_progress")
        await SiteScrapeTask.get_motor_collection().update_many(
            {"site_id": self.site.id, "status": {"$in": [TaskStatus.IN_PROGRESS]}},
            {"$set": {"status": TaskStatus.CANCELED}},
        )
        await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))

    # TODO: Add error handling, transaction.
    async def set_last_collected(self, task) -> CollectionResponse:
        """Update last_collected_date for retrieved_docs and retrieved_doc's doc."""
        print("setting retrieved_docs")
        retrieved_documents: list[RetrievedDocument] = (
            await RetrievedDocument.find_many({"_id": {"$in": task.retrieved_document_ids}})
            .sort("-first_collected_date")
            .to_list()
        )
        if not retrieved_documents:
            self.logger.info(f"No retrieved_docs for site_scrape_task[{task.id}]")
            return CollectionResponse(errors=[])

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
        return CollectionResponse(errors=[])

    async def process_work_lists(self) -> CollectionResponse:
        """
        Go through every queued task's work_list and process each action.
        Set state for site, scrape_tasks, work_items, doc_doc and retr_doc.
        """
        print("processing work_list")
        work_list_response: Type[CollectionResponse] = CollectionResponse()
        queued_site_tasks: List[SiteScrapeTask] = await self.fetch_all_queued()

        for queued_site_task in queued_site_tasks:
            for work_item in queued_site_task.work_list:
                work_item_response: CollectionResponse = await self.process_work_item(
                    target_task=queued_site_task, work_item=work_item
                )
                # TODO: What happens on work item error.
                if work_item_response.errors:
                    work_list_response.add_error(work_item_response)
                    print("got errors")
                    print("work_item_error")
                    print(work_item_response)
                    # TODO: Filter an update existing error.
        if work_list_response.errors:
            print("!!!! work_list_errors !!!!")
            print(work_list_response)

        return work_list_response

    async def process_work_item(
        self, target_task: SiteScrapeTask, work_item: ManualWorkItem
    ) -> CollectionResponse:
        """
        TODO: go through each work_list item, set finished or failed.
        set associations depending on work_list item action.
        """
        result = CollectionResponse()
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
        return result
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
