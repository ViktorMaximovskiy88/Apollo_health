import asyncio

from backend.common.db.init import init_db
from backend.common.models.work_queue import SubmitAction, WorkQueue


async def create_default_work_queues():
    if await WorkQueue.count():
        return

    await WorkQueue(
        name="Classification",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={"classification_status": "QUEUED"},
        sort_query=["last_collected_date"],
        user_query={"roles": {"$in": ["admin", "triage"]}},
        submit_actions=[
            SubmitAction(
                label="Submit", submit_action={"classification_status": "APPROVED"}, primary=True
            ),
            SubmitAction(
                label="Hold",
                reassignable=True,
                require_comment=True,
                submit_action={"classification_status": "HOLD"},
            ),
        ],
    ).save()
    await WorkQueue(
        name="Classification Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={"classification_status": "HOLD"},
        sort_query=["last_collected_date"],
        user_query={"roles": {"$in": ["admin"]}},
        submit_actions=[
            SubmitAction(
                label="Approve", submit_action={"classification_status": "APPROVED"}, primary=True
            ),
            SubmitAction(label="Back To Queue", submit_action={"classification_status": "QUEUED"}),
        ],
    ).save()

    await WorkQueue(
        name="Content Extraction",
        update_model_name="UpdateDocDocument",
        collection_name="DocDocument",
        sort_query=["last_collected_date"],
        frontend_component="ContentExtractionApprovalPage",
        document_query={
            "content_extraction_task_id": {"$ne": None},
            "content_extraction_status": "QUEUED",
        },
        user_query={"roles": {"$in": ["admin", "triage"]}},
        submit_actions=[
            SubmitAction(
                label="Submit",
                submit_action={"content_extraction_status": "APPROVED"},
                primary=True,
            ),
            SubmitAction(label="Hold", submit_action={"content_extraction_status": "HOLD"}),
        ],
    ).save()
    await WorkQueue(
        name="Content Extraction Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        sort_query=["last_collected_date"],
        frontend_component="ContentExtractionApprovalPage",
        document_query={
            "content_extraction_task_id": {"$ne": None},
            "content_extraction_status": "HOLD",
        },
        user_query={"roles": {"$in": ["admin"]}},
        submit_actions=[
            SubmitAction(
                label="Approve",
                submit_action={"content_extraction_status": "APPROVED"},
                primary=True,
            ),
            SubmitAction(
                label="Back To Queue", submit_action={"content_extraction_status": "QUEUED"}
            ),
        ],
    ).save()


async def execute():
    await init_db()
    await create_default_work_queues()


if __name__ == "__main__":
    asyncio.run(execute())
