from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from ..models.schemas import VehicleCreate, VehicleCreateOut, VehicleOut
from ..models.models import Vehicle
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

import base64

router = APIRouter(
    prefix='/vehicles',
    tags=['Vehicles']
)


@router.get('/', response_model=Page[VehicleOut], status_code=status.HTTP_200_OK)
def get_all_vehicles(
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
        license_plate: Optional[str] = Query(default=None)
):
    query = db.query(Vehicle).filter(Vehicle.owner_id == current_active_user.id)
    if license_plate is not None:
        query = query.filter(Vehicle.license_plate.ilike(f'{license_plate.lower()}%'))
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.post('/', response_model=VehicleCreateOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    try:
        new_vehicle = Vehicle(**vehicle.model_dump())
        new_vehicle.owner = current_active_user
        new_vehicle.created_at = datetime.utcnow()
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        return new_vehicle
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vehicle already exists')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@router.get('/{vehicle_id}', response_model=VehicleOut, status_code=status.HTTP_200_OK)
def get_vehicle_id(vehicle_id: int, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if (not vehicle) or vehicle.owner_id != current_active_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    return vehicle


@router.delete('/{vehicle_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    if vehicle.owner_id != current_active_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    db.delete(vehicle)
    db.commit()
    return
