from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from ..models.schemas import ActivityLogOut
from ..models.models import ActivityLog, Vehicle
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/activity_logs',
    tags=['ActivityLogs']
)


@router.get('/', response_model=Page[ActivityLogOut], status_code=status.HTTP_200_OK)
def get_parking_lot_activity_logs(
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
        fromtime: int = Query(default=0, ge=0),
        totime: int = Query(default_factory=lambda: int(datetime.utcnow().timestamp()), ge=0),
        sort: str = Query(default='desc', regex='^(desc|asc)$')
):
    from_timestamp = datetime.fromtimestamp(fromtime)
    to_timestamp = datetime.fromtimestamp(totime)
    order_by = ActivityLog.timestamp.desc() if sort == 'desc' else ActivityLog.timestamp.asc()
    return paginate(db.query(ActivityLog)
                    .join(ActivityLog.vehicle)
                    .filter(Vehicle.owner_id == current_active_user.id,
                            from_timestamp <= ActivityLog.timestamp,
                            ActivityLog.timestamp <= to_timestamp)
                    .order_by(order_by))


@router.get('/{activity_log_id}', response_model=ActivityLogOut, status_code=status.HTTP_200_OK)
def get_activity_log_by_id(activity_log_id: int, current_active_user: CurrentActiveUserDependency,
                           db: DatabaseDependency):
    activity_log = db.query(ActivityLog).filter(ActivityLog.id == activity_log_id).first()
    if not activity_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Activity log not found')
    if activity_log.vehicle_id not in [v.id for v in current_active_user.vehicles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    return activity_log
