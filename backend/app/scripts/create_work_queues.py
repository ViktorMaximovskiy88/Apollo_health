import asyncio
from datetime import datetime, timezone

from backend.common.db.init import init_db
from backend.common.models.work_queue import SubmitAction, WorkQueue


async def classification_queues():
    wq = WorkQueue(
        name="Classification 2023",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "final_effective_date": {"$gte": datetime(2023, 1, 1, tzinfo=timezone.utc)},
            "priority": {"$gt": 0},
            "classification_status": "QUEUED",
        },
        sort_query=["-priority", "final_effective_date"],
        user_query={"roles": {"$in": ["admin", "classification"]}},
        submit_actions=[
            SubmitAction(
                label="Hold",
                reassignable=True,
                require_comment=True,
                dest_queue="Classification Hold",
                submit_action={"classification_status": "HOLD"},
                hold_types=[
                    "Source Hub Issue",
                    "Reconfig Focus Tags",
                    "Medical Codes (J/CPT)",
                    "Spanish / Other Language",
                    "Integration Send Back",
                    "Document Preview Error",
                    "SH DB Focus Tags",
                    "Duplicate J Codes",
                    "Document Preview Error",
                ],
            ),
            SubmitAction(
                label="Submit",
                submit_action={"classification_status": "APPROVED", "classification_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)
    wq = WorkQueue(
        name="Classification",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "final_effective_date": {"$lt": datetime(2023, 1, 1, tzinfo=timezone.utc)},
            "classification_status": "QUEUED",
            "priority": {"$gt": 0},
        },
        sort_query=["-priority", "final_effective_date"],
        user_query={"roles": {"$in": ["admin", "classification"]}},
        submit_actions=[
            SubmitAction(
                label="Hold",
                reassignable=True,
                require_comment=True,
                dest_queue="Classification Hold",
                submit_action={"classification_status": "HOLD"},
                hold_types=[
                    "Source Hub Issue",
                    "Reconfig Focus Tags",
                    "Medical Codes (J/CPT)",
                    "Spanish / Other Language",
                    "Integration Send Back",
                    "Document Preview Error",
                    "SH DB Focus Tags",
                    "Duplicate J Codes",
                    "Document Preview Error",
                ],
            ),
            SubmitAction(
                label="Submit",
                submit_action={"classification_status": "APPROVED", "classification_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)

    wq = WorkQueue(
        name="Classification Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "classification_status": "HOLD",
            "priority": {"$gt": 0},
        },
        hold_types=[
            "Source Hub Issue",
            "Reconfig Focus Tags",
            "Medical Codes (J/CPT)",
            "Spanish / Other Language",
            "Integration Send Back",
            "Document Preview Error",
            "SH DB Focus Tags",
            "Duplicate J Codes",
            "Document Preview Error",
        ],
        sort_query=["-priority", "final_effective_date"],
        user_query={"roles": {"$in": ["admin", "classification"]}},
        submit_actions=[
            SubmitAction(label="Back To Queue", submit_action={"classification_status": "QUEUED"}),
            SubmitAction(
                label="Approve",
                submit_action={"classification_status": "APPROVED", "classification_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)


async def family_queues():
    wq = WorkQueue(
        name="Document & Payer Family",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "classification_status": "APPROVED",
            "family_status": "QUEUED",
            "priority": {"$gt": 0},
            "therapy_tags.focus": True,
        },
        sort_query=["-priority", "final_effective_date"],
        user_query={"roles": {"$in": ["admin", "family"]}},
        submit_actions=[
            SubmitAction(
                label="Reject Classification",
                submit_action={
                    "classification_status": "HOLD",
                    "family_status": "PENDING",
                },
                require_comment=True,
            ),
            SubmitAction(
                label="Hold",
                reassignable=True,
                require_comment=True,
                dest_queue="Document & Payer Family Hold",
                submit_action={"family_status": "HOLD"},
                hold_types=[
                    "Source Hub Issue",
                    "Backbone Issue",
                    "Integration Send Back",
                    "Sample",
                    "Question",
                ],
            ),
            SubmitAction(
                label="Submit",
                submit_action={"family_status": "APPROVED", "family_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)

    wq = WorkQueue(
        name="Document & Payer Family Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        frontend_component="DocDocumentClassificationPage",
        hold_types=[
            "Source Hub Issue",
            "Backbone Issue",
            "Integration Send Back",
            "Sample",
            "Question",
        ],
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "classification_status": "APPROVED",
            "family_status": "HOLD",
            "priority": {"$gt": 0},
            "therapy_tags.focus": True,
        },
        sort_query=["-priority", "final_effective_date"],
        user_query={"roles": {"$in": ["admin", "family"]}},
        submit_actions=[
            SubmitAction(
                label="Reject Classification",
                submit_action={
                    "classification_status": "HOLD",
                    "family_status": "PENDING",
                },
                require_comment=True,
            ),
            SubmitAction(label="Back To Queue", submit_action={"family_status": "QUEUED"}),
            SubmitAction(
                label="Approve",
                submit_action={"family_status": "APPROVED", "family_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)


async def translation_config_queues():
    wq = WorkQueue(
        name="Translation Config",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        sort_query=["-priority", "final_effective_date"],
        frontend_component="DocDocumentClassificationPage",
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "classification_status": "APPROVED",
            "family_status": "APPROVED",
            "content_extraction_status": "QUEUED",
            "priority": {"$gt": 0},
        },
        user_query={"roles": {"$in": ["admin", "translation"]}},
        submit_actions=[
            SubmitAction(
                label="Reject Classification",
                submit_action={
                    "classification_status": "HOLD",
                    "family_status": "PENDING",
                },
                require_comment=True,
            ),
            SubmitAction(
                label="Reject Family",
                submit_action={
                    "family_status": "HOLD",
                    "content_extraction_status": "PENDING",
                },
                require_comment=True,
            ),
            SubmitAction(
                label="Hold",
                reassignable=True,
                require_comment=True,
                dest_queue="Translation Config Hold",
                submit_action={"content_extraction_status": "HOLD"},
                hold_types=["Integration Send Back"],
            ),
            SubmitAction(
                label="Submit",
                submit_action={"content_extraction_status": "APPROVED", "extraction_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)

    wq = WorkQueue(
        name="Translation Config Hold",
        collection_name="DocDocument",
        update_model_name="UpdateDocDocument",
        sort_query=["-priority", "final_effective_date"],
        frontend_component="DocDocumentClassificationPage",
        hold_types=["Integration Send Back"],
        document_query={
            "first_collected_date": {"$gte": datetime(2022, 12, 28, tzinfo=timezone.utc)},
            "family_status": "APPROVED",
            "classification_status": "APPROVED",
            "content_extraction_status": "HOLD",
            "priority": {"$gt": 0},
        },
        user_query={"roles": {"$in": ["admin", "translation"]}},
        submit_actions=[
            SubmitAction(
                label="Reject Classification",
                submit_action={
                    "classification_status": "HOLD",
                    "family_status": "PENDING",
                },
                require_comment=True,
            ),
            SubmitAction(
                label="Reject Family",
                submit_action={
                    "family_status": "HOLD",
                    "content_extraction_status": "PENDING",
                },
                require_comment=True,
            ),
            SubmitAction(
                label="Back To Queue", submit_action={"content_extraction_status": "QUEUED"}
            ),
            SubmitAction(
                label="Approve",
                submit_action={"content_extraction_status": "APPROVED", "extraction_hold_info": []},
                primary=True,
            ),
        ],
    )
    await WorkQueue.find({"name": wq.name}).upsert({"$set": wq.dict()}, on_insert=wq)


async def create_default_work_queues():
    if await WorkQueue.count():
        return

    await classification_queues()
    await family_queues()
    await translation_config_queues()


async def execute():
    await init_db()

    await classification_queues()
    await family_queues()
    await translation_config_queues()


if __name__ == "__main__":
    asyncio.run(execute())
