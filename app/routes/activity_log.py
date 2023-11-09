from fastapi import APIRouter, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from ..models.schemas import ActivityLogOut
from ..models.models import ActivityLog
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/activity_logs',
    tags=['ActivityLogs']
)


@router.get('/', response_model=Page[ActivityLogOut], status_code=status.HTTP_200_OK)
def get_parking_lot_activity_logs(current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    return paginate(db.query(ActivityLog)
                    .where(ActivityLog.user_id == current_active_user.id)
                    .order_by(ActivityLog.created_at.desc()))


@router.get('/{activity_log_id}', response_model=ActivityLogOut, status_code=status.HTTP_200_OK)
def get_activity_log_id(activity_log_id: int, current_active_user: CurrentActiveUserDependency, db:DatabaseDependency):
    activity_log = db.query(ActivityLog).filter(ActivityLog.id == activity_log_id).first()
    if not activity_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Activity log not found')
    if activity_log.user_id != current_active_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    return activity_log
