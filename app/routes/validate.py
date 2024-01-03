import os

from fastapi import APIRouter, Depends, HTTPException, status
import requests

from app.dependencies.camera import CameraDependency
from app.dependencies.db_connection import DatabaseDependency
from app.models.models import Vehicle, ActivityLog
from app.models.schemas import ValidateModel, ParkingSpaceOut

router = APIRouter(
    prefix='/validate',
    tags=['validate']
)


@router.post('/in', response_model=ParkingSpaceOut, status_code=status.HTTP_200_OK)
def validate_in(
    camera: CameraDependency,
    db: DatabaseDependency,
    info: ValidateModel
):
    license_plate = info.license_plate
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not registered')
    if vehicle.owner_id != info.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Vehicle not owned by user')

    vehicle_type = vehicle.vehicle_type
    parking_lot_id = camera.parking_lot_id
    free_space = requests.get(f'{os.getenv("PARKING_LOT_SPACE_SERVICE_URL")}/parking_lots', params={
        'parking_lot_id': parking_lot_id,
    }).json()[vehicle_type]['free']
    if free_space == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parking lot is full')

    parking_space_list = requests.get(f'{os.getenv("PARKING_LOT_SPACE_SERVICE_URL")}/recommend', params={
        'parking_lot_id': parking_lot_id,
        'vehicle_type': vehicle_type,
    })
    if parking_space_list.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Fail to get parking space')
    parking_space = parking_space_list.json()[0]

    response = requests.post('http://localhost:8000/reserve', json={
        'parking_space_id': parking_space['id'],
        'vehicle_id': vehicle.id,
    })
    if response.status_code != 204:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Fail to reserve parking space')

    activity_log = ActivityLog(
        activity_type='in',
        vehicle_id=vehicle.id,
        parking_lot_id=parking_lot_id,
        timestamp=info.timestamp,
    )
    db.add(activity_log)
    db.commit()
    return parking_space


@router.post('/out', status_code=status.HTTP_204_NO_CONTENT)
def validate_out(
    camera: CameraDependency,
    db: DatabaseDependency,
    info: ValidateModel
):
    license_plate = info.license_plate
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not registered')
    if vehicle.owner_id != info.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Vehicle not owned by user')
    activity_log = ActivityLog(
        activity_type='in',
        vehicle_id=vehicle.id,
        parking_lot_id=camera.parking_lot_id,
        timestamp=info.timestamp,
    )
    db.add(activity_log)
    db.commit()
    return
