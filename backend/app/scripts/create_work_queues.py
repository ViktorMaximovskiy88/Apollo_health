import asyncio

from backend.common.db.init import init_db
from backend.common.models.work_queue import SubmitAction, WorkQueue


async def create_default_work_queues():
    triage = WorkQueue(
        name="Triage",
        document_query={ 'triage_status': 'QUEUED' },
        user_query={ 'roles': { '$in': [ "admin", "triage" ] } },
        submit_actions=[
            SubmitAction(label="Submit", submit_action={ 'triage_status': 'PENDING_APPROVAL' }, primary=True),
            SubmitAction(label="Hold", submit_action={ 'triage_status': 'HOLD' }),
        ],
    )
    triage_hold = WorkQueue(
        name="Triage Hold",
        document_query={ 'triage_status': 'HOLD' },
        user_query={ 'roles': { '$in': [ "admin" ] } },
        submit_actions=[
            SubmitAction(label="Approve", submit_action={ 'triage_status': 'APPROVED' }, primary=True),
            SubmitAction(label="Back To Queue", submit_action={ 'triage_status': 'QUEUED' }),
        ],
    )
    approval = WorkQueue(
        name="Triage Approval",
        document_query={ 'triage_status': 'PENDING_APPROVAL' },
        user_query={ 'roles': { '$in': [ "admin" ] } },
        submit_actions=[
            SubmitAction(label="Approve", submit_action={ 'triage_status': 'APPROVED' }, primary=True),
            SubmitAction(label="Reject", submit_action={ 'triage_status': 'QUEUED' }),
        ],
    )
    approved = WorkQueue(
        name="Triage Approval",
        document_query={ 'triage_status': 'APPROVED' },
        user_query={ 'roles': { '$in': [ "admin" ] } },
        submit_actions=[],
    )
    await triage_hold.save()
    await approved.save()
    #await triage.save()
    #await approval.save()


async def execute():
    await init_db()
    await create_default_work_queues()


if __name__ == "__main__":
    asyncio.run(execute())
