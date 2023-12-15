from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.devices import CameraAuthDependency, SensorAuthDependency
from app.models.models import ParkingSpace, Vehicle
from app.models.schemas import ParkingSpaceOut

router = APIRouter(
    prefix='/parking_spaces'
)


@router.get('/free', response_model=ParkingSpaceOut, status_code=status.HTTP_200_OK)
def get_free_parking_space(
        db: DatabaseDependency,
        camera: CameraAuthDependency
):
    parking_lot_id = camera.parking_lot_id
    parking_space = (db.query(ParkingSpace)
                     .filter(ParkingSpace.parking_lot_id == parking_lot_id)
                     .filter(ParkingSpace.vehicle_id.is_(None))
                     .first())
    if not parking_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No parking space found')
    if parking_space.vehicle_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Parking space is occupied')
    return parking_space


@router.put('/ack', status_code=status.HTTP_204_NO_CONTENT)
def acknowledge_parking_space(
        db: DatabaseDependency,
        sensor: SensorAuthDependency,
        direction: str = Query(regex='^(in|out)$'),
        license_plate: Optional[str] = Query(default=None)
):
    parking_space = sensor.parking_space
    if direction == 'in':
        if license_plate is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='license_plate is required')
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
        if vehicle is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
        parking_space.vehicle_id = vehicle.id
    else:
        if license_plate is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unexpected field license_plate')
        parking_space.vehicle_id = None
    db.commit()
    db.refresh(parking_space)
    return
