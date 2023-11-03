from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import ActivityLogCreate, ActivityLogOut
from ..models.models import ActivityLog
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/api/activity_logs',
    tags=['ActivityLogs']
)

@router.get('/api/', response_model=List[ActivityLogOut], status_code=status.HTTP_200_OK)
def get_all_activity_logs(current_user: CurrentActiveUserDependency, db:DatabaseDependency):
    query = db.query(ActivityLog).filter(ActivityLog.is_deleted == False)
    if not current_user.is_superuser:
        query = query.filter(ActivityLog.owner_id == current_user.id)
    activity_logs = query.all()
    return activity_logs

@router.post('/api/', response_model=ActivityLogOut, status_code=status.HTTP_201_CREATED)
def create_activity_log(activity_log: ActivityLogCreate, current_user: CurrentActiveUserDependency, db:DatabaseDependency):
    new_activity_log = ActivityLog(**activity_log.model_dump())
    new_activity_log.owner_id = current_user.id
    db.add(new_activity_log)
    db.commit()
    db.refresh(new_activity_log)
    return new_activity_log
