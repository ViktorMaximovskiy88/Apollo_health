import datetime
from pymongo import ReturnDocument
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from backend.common.models.document_assessment import DocumentAssessment, DocumentAssessmentUpdate
from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.models.work_queue import WorkQueue

router = APIRouter(
    prefix="/assessments",
    tags=["DocumentAssessments"],
)


async def get_target(id: PydanticObjectId):
    assessment = await DocumentAssessment.get(id)
    if not assessment:
        raise HTTPException(
            detail=f"Assessment {id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return assessment

async def get_work_queue(work_queue_id: PydanticObjectId) -> WorkQueue:
    queue = await WorkQueue.get(work_queue_id)
    if not queue:
        raise HTTPException(
            detail=f"Work Queue {id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return queue

@router.get("/", response_model=list[DocumentAssessment])
async def read_document_assessments(
    work_queue: WorkQueue = Depends(get_work_queue),
    current_user: User = Depends(get_current_user),
):
    assessments = await DocumentAssessment.find_many(work_queue.document_query).to_list()
    return assessments

@router.get("/{id}", response_model=DocumentAssessment)
async def read_document_assessment(
    target: DocumentAssessment = Depends(get_target),
    current_user: User = Depends(get_current_user),
):
    return target

@router.put("/", response_model=DocumentAssessment, status_code=status.HTTP_201_CREATED)
async def create_document_assessment(
    assessment: DocumentAssessment,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    return await create_and_log(logger, current_user, assessment)

@router.post("/{id}", response_model=DocumentAssessment)
async def update_document_assessment(
    updates: DocumentAssessmentUpdate,
    target: DocumentAssessment = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated

@router.post("/{assessment_id}/take")
async def take_document_assessment(
    work_queue_id: PydanticObjectId,
    assessment_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    # Check if you already own the lock, if so just bump the expiry
    now = datetime.datetime.now()
    ten_seconds_from_now = now + datetime.timedelta(seconds=10)
    await DocumentAssessment.find_one({ '_id': assessment_id }).update({ '$pull': { 'locks': { 'expires': { '$lt': now } } } })

    already_owned = await DocumentAssessment.get_motor_collection().find_one_and_update(
        {
            '_id': assessment_id,
            'locks': {
                '$elemMatch': {
                    'work_queue_id': work_queue_id,
                    'user_id': current_user.id,
                    'expires': { '$gt': now }
                }
            }
        },
        {
            '$set': { 'locks.$.expires': ten_seconds_from_now },
        },
        return_document=ReturnDocument.AFTER
    )
    if already_owned:
        assessment = DocumentAssessment.parse_obj(already_owned)
        lock = next(filter(lambda l: l.work_queue_id == work_queue_id and l.expires > now, assessment.locks))
        return { 'acquired_lock': True, 'lock': lock}

    # Check if anyone owns the lock, if no take it
    acquired = await DocumentAssessment.get_motor_collection().find_one_and_update(
        {
            '_id': assessment_id,
            'locks': {
                '$not': {
                    '$elemMatch': {
                        'work_queue_id': work_queue_id,
                        'expires': { '$gt': now }
                    }
                }
            }
        },
        {
            '$addToSet': {
                'locks': {
                    'work_queue_id': work_queue_id,
                    'expires': ten_seconds_from_now,
                    'user_id': current_user.id
                }
            },
        },
        return_document=ReturnDocument.AFTER
    )
    if acquired:
        assessment = DocumentAssessment.parse_obj(acquired)
        lock = next(filter(lambda l: l.work_queue_id == work_queue_id and l.expires > now, assessment.locks))
        return { 'acquired_lock': True, 'lock': lock }

    print('lock already taken')
    assessment = await get_target(assessment_id)
    lock = next(filter(lambda l: l.work_queue_id == work_queue_id and l.expires > now, assessment.locks))
    return { 'acquired_lock': False, 'lock': lock }
