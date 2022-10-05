import logging
import pprint
from datetime import datetime
from xmlrpc.client import Boolean

from beanie.odm.operators.update.general import Set
from pydantic import BaseModel

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import ManualWorkItem, SiteScrapeTask


# TODO: Define frontend error handler.
class WorkItemError(BaseModel):
    success: bool | None = True
    errors: dict | None = {}  # field_name: field_value


class WorkListError(BaseModel):
    success: bool | None = True
    errors: list | None = list[WorkItemError]


class SiteTasksService:
    def __init__(self, site: Site) -> None:
        self.site = site
        self.logger = logging
        self.pp = pprint.PrettyPrinter(depth=4)
        self.queued_statuses = [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]

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

    # Stop collecting all queued tasks.
    # Cancel each queued task, then set site.last_run_status to finished.
    async def stop_collecting(self) -> Boolean:
        if self.site.collection_method == CollectionMethod.Manual:
            result = await self.cancel_manual()
        else:
            result = await self.cancel_queued()
        print("result is")
        print(result)
        await self.site.update(Set({Site.last_run_status: TaskStatus.FINISHED}))

    # Cancel all manual tasks.
    # TODO: go through each work_list item, set finished or failed.
    # set associations depending on work_list item action.
    async def cancel_manual(self) -> Boolean:
        last_queued_task = await self.fetch_last_queued()

        # Do not have queued tasks. Cancel in case task created during execution.
        if not last_queued_task:
            return True
        # Have unfinished queued task but no collected documents.
        if last_queued_task.documents_found == 0:
            await self.cancel_in_progress()
        # Have unfinished task with collected documents.
        # TODO: Add better error handling / transactions.
        else:
            await self.process_work_lists()
            await self.cancel_queued()
            await self.set_last_collected(last_queued_task)
        return True

    # Cancel all queued site tasks.
    async def cancel_queued(self) -> SiteScrapeTask:
        print("canceling queued")
        await SiteScrapeTask.get_motor_collection().update_many(
            {
                "site_id": self.site.id,
                "status": {"$in": self.queued_statuses},
            },
            {"$set": {"status": TaskStatus.CANCELING}},
        )
        await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))

    # Cancel only tasks which are in progress.
    # Since a doc was never collected, set TaskStatus.CANCELED instead of CANCELING.
    async def cancel_in_progress(self) -> SiteScrapeTask:
        print("canceling in_progress")
        await SiteScrapeTask.get_motor_collection().update_many(
            {"site_id": self.site.id, "status": {"$in": [TaskStatus.IN_PROGRESS]}},
            {"$set": {"status": TaskStatus.CANCELED}},
        )
        await self.site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))

    # Update last_collected_date for retrieved_docs and retrieved_doc's doc.
    async def set_last_collected(self, task) -> Boolean:
        print("set_retrieved_collected")
        retrieved_documents: list[RetrievedDocument] = (
            await RetrievedDocument.find_many({"_id": {"$in": task.retrieved_document_ids}})
            .sort("-first_collected_date")
            .to_list()
        )
        if not retrieved_documents:
            self.logger.info(f"No retrieved_docs for site_scrape_task[{task.id}]")
            return True

        # Update last_collected_date for each retrieved_doc and it's doc.
        for r_doc in retrieved_documents:
            print("set retrieved_docs")
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
        return True

    # For each site_scrape_tasks work_list, process all work_item actions.
    async def process_work_lists(self) -> WorkListError:
        print("processing work_list")
        work_list_errors = WorkListError
        queued_site_tasks = await self.fetch_all_queued()
        for queued_site_task in queued_site_tasks:
            for work_item in queued_site_task.work_list:
                work_item_error = await self.process_work_item(
                    target_task=queued_site_task, work_item=work_item
                )
                if work_item_error:
                    print("got errors")
                    print("work_item_error")
                    print(work_item_error)
                    work_list_errors.success = False
                    work_list_errors.errors.append(work_item_error)

        return work_list_errors

    async def process_work_item(
        self, target_task: SiteScrapeTask, work_item: ManualWorkItem
    ) -> WorkItemError:
        print("processing work_item")
        print(work_item)
        work_item_header_msg = (
            f"work_item selected [{work_item.selected}] doc_id: [{work_item.document_id}] "
            f"retrieved_document_id [{work_item.retrieved_document_id}] not found."
        )
        print("error_header is ")
        print(work_item_header_msg)

        # index = next(i for i, wi in enumerate(target_task.work_list) if wi.document_id == doc_id)
        # task_updates["work_list"][index] = updates.dict()
        # updated = await update_and_log_diff(logger, current_user, target_task, task_updates)

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
        match work_item.selected:
            case "NOT_FOUND":
                self.logger.info(f"{work_item_header_msg}")
            case "FOUND":
                self.logger.info(f"{work_item_header_msg}")
            case _:
                self.logger.info(f"{work_item_header_msg}")
