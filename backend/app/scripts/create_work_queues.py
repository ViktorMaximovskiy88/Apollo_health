import asyncio

from backend.common.db.init import init_db
from backend.common.models.work_queue import SubmitAction, WorkQueue


async def classification_queues():
    await WorkQueue(
        name="Classification",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={"classification_status": "QUEUED"},
        sort_query=["final_effective_date"],
        user_query={"roles": {"$in": ["admin", "classification"]}},
        submit_actions=[
            SubmitAction(
                label="Hold",
                reassignable=True,
                require_comment=True,
                submit_action={"classification_status": "HOLD"},
            ),
            SubmitAction(
                label="Submit", submit_action={"classification_status": "APPROVED"}, primary=True
            ),
        ],
    ).save()
    await WorkQueue(
        name="Classification Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={"classification_status": "HOLD"},
        sort_query=["final_effective_date"],
        user_query={"roles": {"$in": ["admin", "classification"]}},
        submit_actions=[
            SubmitAction(label="Back To Queue", submit_action={"classification_status": "QUEUED"}),
            SubmitAction(
                label="Approve", submit_action={"classification_status": "APPROVED"}, primary=True
            ),
        ],
    ).save()


async def family_queues():
    await WorkQueue(
        name="Document & Payer Family",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={"classification_status": "APPROVED", "family_status": "QUEUED"},
        sort_query=["final_effective_date"],
        user_query={"roles": {"$in": ["admin", "family"]}},
        submit_actions=[
            SubmitAction(label="Hold", submit_action={"family_status": "HOLD"}),
            SubmitAction(
                label="Submit",
                reassignable=True,
                require_comment=True,
                submit_action={"family_status": "APPROVED"},
                primary=True,
            ),
        ],
    ).save()
    await WorkQueue(
        name="Document & Payer Family Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={"classification_status": "APPROVED", "family_status": "HOLD"},
        sort_query=["final_effective_date"],
        user_query={"roles": {"$in": ["admin", "family"]}},
        submit_actions=[
            SubmitAction(label="Back To Queue", submit_action={"family_status": "QUEUED"}),
            SubmitAction(
                label="Approve", submit_action={"family_status": "APPROVED"}, primary=True
            ),
        ],
    ).save()


async def translation_config_queues():
    await WorkQueue(
        name="Translation Config",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        sort_query=["final_effective_date"],
        frontend_component="DocDocumentClassificationPage",
        document_query={
            "classification_status": "APPROVED",
            "family_status": "APPROVED",
            "content_extraction_status": "QUEUED",
        },
        user_query={"roles": {"$in": ["admin", "translation"]}},
        submit_actions=[
            SubmitAction(label="Hold", submit_action={"content_extraction_status": "HOLD"}),
            SubmitAction(
                label="Submit",
                submit_action={"content_extraction_status": "APPROVED"},
                primary=True,
            ),
        ],
    ).save()
    await WorkQueue(
        name="Translation Config Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        sort_query=["final_effective_date"],
        frontend_component="DocDocumentClassificationPage",
        document_query={"content_extraction_status": "HOLD"},
        user_query={"roles": {"$in": ["admin", "translation"]}},
        submit_actions=[
            SubmitAction(
                label="Back To Queue", submit_action={"content_extraction_status": "QUEUED"}
            ),
            SubmitAction(
                label="Approve",
                submit_action={"content_extraction_status": "APPROVED"},
                primary=True,
            ),
        ],
    ).save()


async def create_default_work_queues():
    await WorkQueue.delete_all()
    if await WorkQueue.count():
        return

    await classification_queues()
    await family_queues()
    await translation_config_queues()


async def execute():
    await init_db()
    await create_default_work_queues()


if __name__ == "__main__":
    asyncio.run(execute())
