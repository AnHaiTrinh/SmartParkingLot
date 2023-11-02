from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import VehicleCreate, VehicleUpdate, VehicleCreateOut, VehicleOut
from ..models.models import Vehicle
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

import base64

router = APIRouter(
    prefix='/vehicles',
    tags=['Vehicles']
)

@router.get('/', response_model=List[VehicleOut], status_code=status.HTTP_200_OK)
def get_all_vehicles(_: CurrentActiveUserDependency, db: DatabaseDependency):
    vehicles = db.query(Vehicle).filter(Vehicle.is_deleted == False).all()
    return vehicles

@router.post('/', response_model=VehicleCreateOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate,current_user: CurrentActiveUserDependency, db: DatabaseDependency):
    try:
        new_vehicle = Vehicle(**vehicle.model_dump())
        existing_vehicle = db.query(Vehicle).filter(Vehicle.license_plate == new_vehicle.license_plate, Vehicle.is_deleted == True).first()
        if existing_vehicle:
            i = 1
            new_license_plate = f'{new_vehicle.license_plate} ({i})'
            while db.query(Vehicle).filter(Vehicle.license_plate == new_license_plate).first():
                i += 1
                new_license_plate = f'{new_vehicle.license_plate} ({i})'
            existing_vehicle.license_plate = new_license_plate

        new_vehicle.owner_id = current_user.id
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        return new_vehicle
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='vehicle already exists')

@router.get('/{vehicle_id}', response_model=VehicleOut, status_code=status.HTTP_200_OK)
def get_vehicle_id(vehicle_id: int,_: CurrentActiveUserDependency, db: DatabaseDependency):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted == False).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    return vehicle

@router.put('/{vehicle_id}', response_model=VehicleOut, status_code=status.HTTP_200_OK)
def update_vehicle(vehicle_id: int,
                   vehicle_update: VehicleUpdate,
                   _: CurrentActiveUserDependency,
                   db:DatabaseDependency):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted == False).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    vehicle.license_plate = vehicle_update.license_plate
    vehicle.vehicle_type = vehicle.vehicle_type
    vehicle.payment_info = vehicle.payment_info
    vehicle.updated_at = datetime.now()
    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.delete('/{vehicle_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int,_: CurrentActiveUserDependency, db: DatabaseDependency):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted == False).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    vehicle.is_deleted = True
    vehicle.deleted_at = datetime.now()
    db.commit()
    return