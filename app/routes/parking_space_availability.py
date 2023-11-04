from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import ParkingSpaceAvailabilityCreate, ParkingSpaceAvailabilityUpdate, ParkingSpaceAvailabilityCreateOut, ParkingSpaceAvailabilityOut
from ..models.models import ParkingSpaceAvailability, ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/parking_space_availabilities',
    tags=['ParkingSpaceAvailabilities']
)

@router.get('/{parking_lot_id}', response_model=List[ParkingSpaceAvailabilityOut], status_code=status.HTTP_200_OK)
def get_parking_lot_spaces(parking_lot_id: int, db:DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parking lot not found')
    parking_space_availabilities = db.query(ParkingSpaceAvailability).join(ParkingLot, ParkingLot.id == ParkingSpaceAvailability.parking_lot_id).filter(ParkingSpaceAvailability.is_active == True)
    return parking_space_availabilities

@router.post('/', response_model=ParkingSpaceAvailabilityCreateOut, status_code=status.HTTP_201_CREATED)
def create_parking_space_availability(parking_space_availability: ParkingSpaceAvailabilityCreate, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    new_parking_space_availability = ParkingSpaceAvailability(**parking_space_availability.model_dump())
    existing_parking_lot = db.query(ParkingLot).filter(ParkingLot.id == new_parking_space_availability.parking_lot_id, ParkingLot.is_active == True).first()
    if not existing_parking_lot:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='parking lot not found')
    existing_parking_space_availability = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.parking_lot_id == new_parking_space_availability.parking_lot_id, ParkingSpaceAvailability.vehicle_type == new_parking_space_availability.vehicle_type, ParkingSpaceAvailability.is_active == True).first()
    if existing_parking_space_availability:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='parking space availability already exists')
    db.add(new_parking_space_availability)
    db.commit()
    db.refresh(new_parking_space_availability)
    return new_parking_space_availability

@router.get('/{parking_space_availability_id}', response_model=ParkingSpaceAvailabilityOut, status_code=status.HTTP_200_OK)
def get_parking_space_availability_id(parking_space_availability_id: int, db: DatabaseDependency):
    query = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.id == parking_space_availability_id, ParkingSpaceAvailability.is_active == True)
    parking_space_availability = query.first()
    if not parking_space_availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parking space availability not found')
    return parking_space_availability

@router.put('/{parking_space_availability_id}', response_model=ParkingSpaceAvailabilityOut, status_code=status.HTTP_200_OK)
def update_parking_space_availability(parking_space_availability_id: int, update_parking_space_availability: ParkingSpaceAvailabilityUpdate, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    parking_space_availability = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.id == parking_space_availability_id, ParkingSpaceAvailability.is_active == True).first()
    if not parking_space_availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parking space availability not found')
    parking_space_availability.available_spaces = update_parking_space_availability.available_spaces
    db.commit()
    db.refresh(parking_space_availability)
    return parking_space_availability

@router.delete('/{parking_space_availability_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_space_availability(parking_space_availability_id: int, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    query = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.id == parking_space_availability_id, ParkingSpaceAvailability.is_active == True)
    if not current_active_user.is_superuser:
        query = query.join(ParkingLot, ParkingSpaceAvailability.parking_lot_id == ParkingLot.id)
    parking_space_availability = query.first()
    if not parking_space_availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parking space availability not found')
    parking_space_availability.is_active = False
    parking_space_availability.deleted_at = datetime.now()
    db.commit()