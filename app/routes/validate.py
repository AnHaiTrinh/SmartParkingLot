from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List

from ..models.schemas import ValidateActivityLog, VehicleOut, ActivityLogOut, ParkingLotOut
from ..models.models import ActivityLog, Vehicle, ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/validates',
    tags=['Validates']
)

@router.post('/validate', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_log(validate_activity_log: ValidateActivityLog, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log.parking_lot_id).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log.license_plate).first()
    if vehicle:
        new_activity_log = ActivityLog(
            user_id=vehicle.owner_id,
            parking_lot_id=validate_activity_log.parking_lot_id,
            activity_type=validate_activity_log.activity_type,
            license_plate=validate_activity_log.license_plate,
            timestamp=validate_activity_log.created_at
        )
        db.add(new_activity_log)
        db.commit()
        return
    else:
        new_vehicle = Vehicle(
            license_plate=validate_activity_log.license_plate,
            vehicle_type=validate_activity_log.vehicle_type,
            owner_id=current_active_user.id,
            created_at=validate_activity_log.created_at
        )
        new_activity_log = ActivityLog(
            user_id=new_vehicle.owner_id,
            parking_lot_id=validate_activity_log.parking_lot_id,
            activity_type=validate_activity_log.activity_type,
            license_plate=validate_activity_log.license_plate,
            timestamp=validate_activity_log.created_at
        )
        db.add(new_vehicle)
        db.add(new_activity_log)
        db.commit()
        return
    
@router.post('/validate-range', status_code=status.HTTP_204_NO_CONTENT)
def validate_activity_logs(validate_activity_logs: List[ValidateActivityLog], current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    new_vehicles = []
    new_activity_logs = []
    for validate_activity_log in validate_activity_logs:
        parking_lot = db.query(ParkingLot).filter(ParkingLot.id == validate_activity_log.parking_lot_id).first()
        if parking_lot:
            vehicle = db.query(Vehicle).filter(Vehicle.license_plate == validate_activity_log.license_plate).first()
            if vehicle:
                new_activity_log = ActivityLog(
                    user_id=vehicle.owner_id,
                    parking_lot_id=validate_activity_log.parking_lot_id,
                    activity_type=validate_activity_log.activity_type,
                    license_plate=validate_activity_log.license_plate,
                    timestamp=validate_activity_log.created_at
                )
                new_activity_logs.append(new_activity_log)
            else:
                new_vehicle = Vehicle(
                    license_plate=validate_activity_log.license_plate,
                    vehicle_type=validate_activity_log.vehicle_type,
                    owner_id=current_active_user.id,
                    created_at=validate_activity_log.created_at
                )
                new_activity_log = ActivityLog(
                    user_id=new_vehicle.owner_id,
                    parking_lot_id=validate_activity_log.parking_lot_id,
                    activity_type=validate_activity_log.activity_type,
                    license_plate=validate_activity_log.license_plate,
                    timestamp=validate_activity_log.created_at
                )
                new_vehicles.append(new_vehicle)
                new_activity_logs.append(new_activity_log)
    db.add_all(new_vehicles)
    db.add_all(new_activity_logs)
    db.commit()
    return