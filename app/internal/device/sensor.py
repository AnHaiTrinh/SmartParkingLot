from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import Sensor, ParkingSpace
from app.models.schemas import SensorCreate, SensorUpdate, SensorOut, SensorCreateOut

router = APIRouter(
    prefix='/sensors'
)


@router.get('/', response_model=Page[SensorOut], status_code=status.HTTP_200_OK)
def get_sensors(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
        parking_lot_id: Optional[int] = Query(default=None),
        parking_space_id: Optional[int] = Query(default=None)
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    if parking_lot_id is not None and parking_space_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot filter by both parking_lot_id and parking_space_id'
        )
    query = db.query(Sensor)
    if parking_lot_id is not None:
        query = query.join(Sensor.parking_space).filter(ParkingSpace.parking_lot_id == parking_lot_id)
    if parking_space_id is not None:
        query = query.filter(Sensor.parking_space_id == parking_space_id)
    if not show_deleted:
        query = query.filter(Sensor.is_active == True)
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.get('/{sensor_id}', response_model=SensorOut, status_code=status.HTTP_200_OK)
def get_sensor_by_id(sensor_id: int, db: DatabaseDependency, current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Sensor not found')
    return sensor


@router.post('/', response_model=SensorCreateOut, status_code=status.HTTP_201_CREATED)
def create_sensor(
        sensor_create: SensorCreate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    sensor = Sensor(**sensor_create.model_dump())
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


@router.put('/{sensor_id}', response_model=SensorOut, status_code=status.HTTP_200_OK)
def update_sensor(
        sensor_id: int,
        sensor_update: SensorUpdate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Sensor not found')
    sensor_update_dict = sensor_update.model_dump(exclude_unset=True)
    for key, value in sensor_update_dict.items():
        setattr(sensor, key, value)
    sensor.updated_at = datetime.now()
    db.commit()
    db.refresh(sensor)
    return sensor


@router.delete('/{sensor_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(db: DatabaseDependency, sensor_id: int, current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Sensor not found')
    sensor.is_active = False
    sensor.deleted_at = datetime.now()
    db.commit()
    return
