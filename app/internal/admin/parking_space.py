from datetime import datetime
from typing import Optional

from fastapi import APIRouter, status, Query, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import ParkingSpace
from app.models.schemas import ParkingSpaceCreate, ParkingSpaceAdminOut, ParkingSpaceUpdate

router = APIRouter(
    prefix='/parking_spaces',
    tags=['ParkingSpaces']
)


@router.get('/', response_model=Page[ParkingSpaceAdminOut], status_code=status.HTTP_200_OK)
def get_parking_spaces(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
        parking_lot_id: Optional[int] = Query(default=None),
        show_occupied: Optional[bool] = Query(default=None)
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    query = db.query(ParkingSpace)
    if not show_deleted:
        query = query.filter(ParkingSpace.is_active == True)
    if parking_lot_id is not None:
        query = query.filter(ParkingSpace.parking_lot_id == parking_lot_id)
    if show_occupied is not None:
        query = query.filter(
            ParkingSpace.vehicle_id.isnot(None) if show_occupied else ParkingSpace.vehicle_id.is_(None))
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.get('/{parking_space_id}', response_model=ParkingSpaceAdminOut, status_code=status.HTTP_200_OK)
def get_parking_space_by_id(parking_space_id: int, db: DatabaseDependency,
                            current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == parking_space_id).first()
    if not parking_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking space not found')
    return parking_space


@router.post('/', response_model=ParkingSpaceAdminOut, status_code=status.HTTP_201_CREATED)
def create_parking_space(
        parking_space_create: ParkingSpaceCreate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    parking_space = ParkingSpace(**parking_space_create.dict())
    db.add(parking_space)
    db.commit()
    db.refresh(parking_space)
    return parking_space


@router.put('/{parking_space_id}', response_model=ParkingSpaceAdminOut, status_code=status.HTTP_200_OK)
def update_parking_space(
        parking_space_id: int,
        parking_space_update: ParkingSpaceUpdate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    parking_space = db.query(ParkingSpace).filter(ParkingSpace.id == parking_space_id).first()
    if not parking_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking space not found')
    parking_space_update_dict = parking_space_update.model_dump(exclude_unset=True)
    for key, value in parking_space_update_dict.items():
        setattr(parking_space, key, value)
    parking_space.updated_at = datetime.now()
    db.commit()
    db.refresh(parking_space)
    return parking_space


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
    parking_space.deleted_at = datetime.now()
    db.commit()
    return
