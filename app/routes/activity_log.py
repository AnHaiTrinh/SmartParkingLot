from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import ActivityLogCreate, ActivityLogOut
from ..models.models import ActivityLog, User, Vehicle, ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/activity_logs',
    tags=['ActivityLogs']
)

@router.get('/{parking_lot_id}', response_model=List[ActivityLogOut], status_code=status.HTTP_200_OK)
def get_parking_lot_activity_logs(parking_lot_id: int, current_active_user: CurrentActiveUserDependency, db:DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot no found")
    query = db.query(ActivityLog).join(ParkingLot, ParkingLot.id == ActivityLog.parking_lot_id)
    if not current_active_user.is_superuser:
        query = query.join(User, ActivityLog.user_id == User.id).filter(User.id == current_active_user.id)
    activity_logs = query.all()
    return activity_logs

@router.post('/', response_model=ActivityLogOut, status_code=status.HTTP_201_CREATED)
def create_activity_log(activity_log: ActivityLogCreate, current_active_user: CurrentActiveUserDependency, db:DatabaseDependency):
    new_activity_log = ActivityLog(**activity_log.model_dump())
    existing_license_plate_user = db.query(Vehicle).filter(Vehicle.license_plate == new_activity_log.license_plate, Vehicle.owner_id == current_active_user.id).first()
    if not existing_license_plate_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='License plate is not registered')
    new_activity_log.user_id = current_active_user.id
    db.add(new_activity_log)
    db.commit()
    db.refresh(new_activity_log)
    return new_activity_log

@router.get('/{activity_log_id}', response_model=ActivityLogOut, status_code=status.HTTP_200_OK)
def get_activity_log_id(activity_log_id: int, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    query = db.query(ActivityLog)
    if not current_active_user.is_superuser:
        query = query.join(User, ActivityLog.user_id == User.id).filter(User.id == current_active_user.id)
    activity_log = query.filter(ActivityLog.id == activity_log_id).first()
    if not activity_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Activity log not found')
    return activity_log  