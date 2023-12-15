from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from ..models.schemas import ParkingLotCreate, ParkingLotUpdate, ParkingLotCreateOut, ParkingLotOut
from ..models.models import ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/parking-lots',
    tags=['ParkingLots']
)


@router.get('/', response_model=Page[ParkingLotOut], status_code=status.HTTP_200_OK)
def get_all_parking_lots(
        db: DatabaseDependency,
        name: Optional[str] = Query(default=None)
):
    query = db.query(ParkingLot).filter(ParkingLot.is_active == True)
    if name is not None:
        query = query.filter(ParkingLot.name.ilike(f'{name.lower()}%'))
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.post('/', response_model=ParkingLotCreateOut, status_code=status.HTTP_201_CREATED)
def create_parking_lot(
        current_active_user: CurrentActiveUserDependency,
        parking_lot: ParkingLotCreate,
        db: DatabaseDependency
):
    try:
        if not current_active_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
        new_parking_lot = ParkingLot(**parking_lot.model_dump())
        db.add(new_parking_lot)
        db.commit()
        db.refresh(new_parking_lot)
        return new_parking_lot
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parking lot already exists')


@router.get('/{parking_lot_id}', response_model=ParkingLotOut, status_code=status.HTTP_200_OK)
def get_parking_lot_by_id(parking_lot_id: int, db: DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    return parking_lot


@router.put('/{parking_lot_id}', response_model=ParkingLotOut, status_code=status.HTTP_200_OK)
def update_parking_lot(parking_lot_id: int,
                       parking_lot_update: ParkingLotUpdate,
                       current_active_user: CurrentActiveUserDependency,
                       db: DatabaseDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    try:
        parking_lot_update_dict = parking_lot_update.model_dump(exclude_unset=True)
        for key, value in parking_lot_update_dict.items():
            if type(value) is dict:
                current_value = getattr(parking_lot, key)
                for sub_key, sub_value in value.items():
                    current_value[sub_key] = sub_value
                setattr(parking_lot, key, current_value)
            else:
                setattr(parking_lot, key, value)
        parking_lot.updated_at = datetime.now()
        db.commit()
        db.refresh(parking_lot)
        return parking_lot
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Name already exists')


@router.delete('/{parking_lot_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_lot(parking_lot_id: int, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parking lot not found')
    parking_lot.is_active = False
    parking_lot.deleted_at = datetime.now()
    db.commit()
    return
