from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List

from ..models.schemas import ValidateActivityLog_Enter, ValidateActivityLog_Exit, VehicleOut, ActivityLogOut, ParkingLotOut
from ..models.models import ActivityLog, Vehicle, ParkingLot, User
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/validates',
    tags=['Validates']
)

@router.post('/validate-enter', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_log_enter(validate_activity_log_enter: ValidateActivityLog_Enter, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if (validate_activity_log_enter.activity_type != 'enter'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Activity type must be enter')
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log_enter.parking_lot_id).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log_enter.license_plate).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    vehicle_owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    if not vehicle_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Waring: Vehicle owner not found')
    new_activity_log = ActivityLog(
        user_id=vehicle_owner.id,
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
        if (validate_activity_log_enter.activity_type != 'enter'):
            continue
        parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log_enter.parking_lot_id).first()
        if not parking_lot:
            continue
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log_enter.license_plate).first()
        if not vehicle:
            continue
        vehicle_owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        if not vehicle_owner:
            continue
        new_activity_log = ActivityLog(
            user_id=vehicle_owner.id,
            parking_lot_id=validate_activity_log_enter.parking_lot_id,
            activity_type=validate_activity_log_enter.activity_type,
            license_plate=validate_activity_log_enter.license_plate,
            timestamp=validate_activity_log_enter.created_at
        )
        new_activity_logs.append(new_activity_log)
    db.add_all(new_activity_logs)
    db.commit()
    return

@router.post('/validate-exit', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_log_exit(validate_activity_log_exit: ValidateActivityLog_Exit, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if (validate_activity_log_exit.activity_type != 'exit'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Activity type must be exit')
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log_exit.parking_lot_id).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log_exit.license_plate).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    vehicle_owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    if not vehicle_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Waring: Vehicle owner not found')
    if (validate_activity_log_exit.user_id != vehicle_owner.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Waring: User not match')
    new_activity_log = ActivityLog(
        user_id=vehicle_owner.id,
        parking_lot_id=validate_activity_log_exit.parking_lot_id,
        activity_type=validate_activity_log_exit.activity_type,
        license_plate=validate_activity_log_exit.license_plate,
        timestamp=validate_activity_log_exit.created_at
    )
    db.add(new_activity_log)
    db.commit()
    return

@router.post('/validate-exit-range', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_log_exits(validate_activity_log_exits: List[ValidateActivityLog_Exit], current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    new_activity_logs = []
    for validate_activity_log_exit in validate_activity_log_exits:
        if (validate_activity_log_exit.activity_type != 'exit'):
            continue
        parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log_exit.parking_lot_id).first()
        if not parking_lot:
            continue
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log_exit.license_plate).first()
        if not vehicle:
            continue
        vehicle_owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        if not vehicle_owner:
            continue
        if (validate_activity_log_exit.user_id != vehicle_owner.id):
            continue
        new_activity_log = ActivityLog(
            user_id=vehicle_owner.id,
            parking_lot_id=validate_activity_log_exit.parking_lot_id,
            activity_type=validate_activity_log_exit.activity_type,
            license_plate=validate_activity_log_exit.license_plate,
            timestamp=validate_activity_log_exit.created_at
        )
        new_activity_logs.append(new_activity_log)
    db.add_all(new_activity_logs)
    db.commit()
    return    