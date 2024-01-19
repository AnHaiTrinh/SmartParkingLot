from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import Sensor, ParkingSpace
from app.models.schemas import SensorOut, SensorCreateOut, SensorCreate

router = APIRouter(
    prefix='/sensors',
    tags=['Sensors']
)


@router.get('/', response_model=Page[SensorOut], status_code=status.HTTP_200_OK)
def get_all_sensors(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
        parking_lot_id: Optional[int] = Query(default=None),
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    query = db.query(Sensor)
    if not show_deleted:
        query = query.filter(Sensor.is_active == True)
    if parking_lot_id is not None:
        query = query.join(Sensor.parking_space).filter(ParkingSpace.parking_lot_id == parking_lot_id)
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.get('/{sensor_id}', response_model=SensorOut, status_code=status.HTTP_200_OK)
def get_sensor_by_id(
        sensor_id: UUID,
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Camera not found')
    return sensor


@router.post('/', response_model=SensorCreateOut, status_code=status.HTTP_201_CREATED)
def create_sensor(
        sensor_create: SensorCreate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    new_sensor = Sensor(**sensor_create.model_dump())
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)
    return new_sensor


@router.delete('/{sensor_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(
        sensor_id: UUID,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Camera not found')
    sensor.is_active = False
    sensor.deleted_at = datetime.utcnow()
    db.commit()
    return
