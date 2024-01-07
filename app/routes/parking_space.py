from datetime import datetime
from typing import Optional

from fastapi import APIRouter, status, Query, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import ParkingSpace
from app.models.schemas import ParkingSpaceCreate, ParkingSpaceCreateOut, ParkingSpaceOut

router = APIRouter(
    prefix='/parking_spaces',
    tags=['ParkingSpaces']
)


@router.get('/', response_model=Page[ParkingSpaceOut], status_code=status.HTTP_200_OK)
def get_parking_spaces(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
        parking_lot_id: Optional[int] = Query(default=None),
        vehicle_type: Optional[str] = Query(default=None, regex='^(car|motorbike|truck)$'),
        show_free_only: bool = Query(default=False)
):
    query = db.query(ParkingSpace)
    if not current_active_user.is_superuser or not show_deleted:
        query = query.filter(ParkingSpace.is_active == True)
    if parking_lot_id is not None:
        query = query.filter(ParkingSpace.parking_lot_id == parking_lot_id)
    if vehicle_type is not None:
        query = query.filter(ParkingSpace.vehicle_type == vehicle_type)
    if show_free_only:
        query = query.filter(ParkingSpace.state == 'free')
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.get('/{parking_space_id}', response_model=ParkingSpaceOut, status_code=status.HTTP_200_OK)
def get_parking_space_by_id(
        parking_space_id: int,
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
):
    parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == parking_space_id).first()
    if not parking_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking space not found')
    if not (parking_space.is_active or current_active_user.is_superuser):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    return parking_space


@router.post('/', response_model=ParkingSpaceCreateOut, status_code=status.HTTP_201_CREATED)
def create_parking_space(
        parking_space_create: ParkingSpaceCreate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    parking_space = ParkingSpace(**parking_space_create.model_dump())
    try:
        db.add(parking_space)
        db.commit()
        db.refresh(parking_space)
        return parking_space
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong')


@router.delete('/{parking_space_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_space(parking_space_id: int, db: DatabaseDependency,
                         current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == parking_space_id,
                                                  ParkingSpace.is_active == True).first()
    if not parking_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking space not found')
    parking_space.is_active = False
    parking_space.deleted_at = datetime.utcnow()
    db.commit()
    return
