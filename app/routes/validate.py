from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List

from ..models.schemas import ValidateActivityLog_Enter, VehicleOut, ActivityLogOut, ParkingLotOut
from ..models.models import ActivityLog, Vehicle, ParkingLot, User
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/validates',
    tags=['Validates']
)

@router.post('/validate-enter', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_log_enter(validate_activity_log_enter: ValidateActivityLog_Enter, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log_enter.parking_lot_id).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log_enter.license_plate).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    vehicler_owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    if not vehicler_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Waring: Vehicle owner not found')
    new_activity_log = ActivityLog(
        user_id=vehicler_owner.id,
        parking_lot_id=validate_activity_log_enter.parking_lot_id,
        activity_type=validate_activity_log_enter.activity_type,
        license_plate=validate_activity_log_enter.license_plate,
        timestamp=validate_activity_log_enter.created_at
    )
    db.add(new_activity_log)
    db.commit()
    return
    
@router.post('/validate-enter-range', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_log_enters(validate_activity_log_enters: List[ValidateActivityLog_Enter], current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    new_activity_logs = []
    for validate_activity_log_enter in validate_activity_log_enters:
        parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log_enter.parking_lot_id).first()
        if not parking_lot:
            continue
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log_enter.license_plate).first()
        if not vehicle:
            continue
        vehicler_owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        if not vehicler_owner:
            continue
        new_activity_log = ActivityLog(
            user_id=vehicler_owner.id,
            parking_lot_id=validate_activity_log_enter.parking_lot_id,
            activity_type=validate_activity_log_enter.activity_type,
            license_plate=validate_activity_log_enter.license_plate,
            timestamp=validate_activity_log_enter.created_at
        )
        new_activity_logs.append(new_activity_log)
    db.add_all(new_activity_logs)
    db.commit()
    return
    