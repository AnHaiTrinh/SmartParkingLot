from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import ParkingSpaceAvailabilityCreate, ParkingSpaceAvailabilityCreateOut, ParkingSpaceAvailabilityOut
from ..models.models import ParkingSpaceAvailability, ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/parking_space_availabilities',
    tags=['ParkingSpaceAvailabilities']
)

@router.get('/', response_model=List[ParkingSpaceAvailabilityOut], status_code=status.HTTP_200_OK)
def get_all_parking_space_availabilities(current_user: CurrentActiveUserDependency, db:DatabaseDependency):
    query = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.is_active == True)
    if not current_user.is_superuser:
        query = query.join(ParkingLot, ParkingSpaceAvailability.parking_lot_id == ParkingLot.id).filter(ParkingLot.owner_id == current_user.id)
    parking_space_availabilities = query.all()
    return parking_space_availabilities

@router.post('/', response_model=ParkingSpaceAvailabilityCreateOut, status_code=status.HTTP_201_CREATED)
def create_parking_space_availability(parking_space_availability: ParkingSpaceAvailabilityCreate, _: CurrentActiveUserDependency, db: DatabaseDependency):
    new_parking_space_availability = ParkingSpaceAvailability(**parking_space_availability.model_dump())
    existing_parking_space_availability = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.parking_lot_id == new_parking_space_availability.parking_lot_id, ParkingSpaceAvailability.vehicle_type == new_parking_space_availability.vehicle_type, ParkingSpaceAvailability.is_active == True).first()
    if existing_parking_space_availability:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='parking space availability already exists')
    db.add(new_parking_space_availability)
    db.commit()
    db.refresh(new_parking_space_availability)
    return new_parking_space_availability

@router.get('/{parking_space_availability_id}', response_model=ParkingSpaceAvailabilityOut, status_code=status.HTTP_200_OK)
def get_parking_space_availability_id(parking_space_availability_id: int, current_user: CurrentActiveUserDependency, db: DatabaseDependency):
    query = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.id == parking_space_availability_id, ParkingSpaceAvailability.is_active == True)
    if not current_user.is_superuser:
        query = query.join(ParkingLot, ParkingSpaceAvailability.parking_lot_id == ParkingLot.id).filter(ParkingLot.owner_id == current_user.id)
    parking_space_availability = query.first()
    if not parking_space_availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parking space availability not found')
    return parking_space_availability

@router.delete('/{parking_space_availability_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_space_availability(parking_space_availability_id: int, current_user: CurrentActiveUserDependency, db: DatabaseDependency):
    query = db.query(ParkingSpaceAvailability).filter(ParkingSpaceAvailability.id == parking_space_availability_id, ParkingSpaceAvailability.is_active == True)
    if not current_user.is_superuser:
        query = query.join(ParkingLot, ParkingSpaceAvailability.parking_lot_id == ParkingLot.id).filter(ParkingLot.owner_id == current_user.id)
    parking_space_availability = query.first()
    if not parking_space_availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='parking space availability not found')
    parking_space_availability.is_active = False
    parking_space_availability.deleted_at = datetime.now()
    db.commit()