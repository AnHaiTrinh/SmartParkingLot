from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, status, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency
from ..models.models import ActivityLog
from ..models.schemas import ActivityLogOut

router = APIRouter()


@router.get('/activity_logs', response_model=Page[ActivityLogOut], status_code=status.HTTP_200_OK)
def get_activity_logs(
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
        fromtime: int = Query(default=0, ge=0),
        totime: int = Query(default_factory=lambda: int(datetime.now().timestamp()), ge=0),
        sort: str = Query(default='desc', regex='^(desc|asc)$'),
        user_id: Optional[int] = Query(default=None),
        parking_lot_id: Optional[int] = Query(default=None),
        license_plate: Optional[str] = Query(default=None)):
    if not current_active_user.is_superuser:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    from_timestamp = datetime.fromtimestamp(fromtime)
    to_timestamp = datetime.fromtimestamp(totime)
    order_by = ActivityLog.timestamp.desc() if sort == 'desc' else ActivityLog.timestamp.asc()
    query = db.query(ActivityLog) \
              .filter(from_timestamp <= ActivityLog.timestamp,
                      ActivityLog.timestamp <= to_timestamp)
    if user_id is not None:
        query = query.filter(ActivityLog.user_id == user_id)
    if parking_lot_id is not None:
        query = query.filter(ActivityLog.parking_lot_id == parking_lot_id)
    if license_plate is not None:
        query = query.filter(ActivityLog.license_plate == license_plate)
    results = paginate(query.order_by(order_by))
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results
