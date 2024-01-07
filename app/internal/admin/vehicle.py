from datetime import datetime
from typing import Optional

from fastapi import APIRouter, status, Query, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import Vehicle
from app.models.schemas import VehicleAdminOut

router = APIRouter(prefix='/vehicles')


@router.get('/', response_model=Page[VehicleAdminOut], status_code=status.HTTP_200_OK)
def get_vehicles(
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
        user_id: Optional[int] = Query(default=None),
        license_plate: Optional[str] = Query(default=None)
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    query = db.query(Vehicle)
    if user_id is not None:
        query = query.filter(Vehicle.owner_id == user_id)
    if license_plate is not None:
        query = query.filter(Vehicle.license_plate == license_plate)
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.put('/track/{vehicle_id}', response_model=VehicleAdminOut, status_code=status.HTTP_200_OK)
def track_vehicles(
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
        vehicle_id: int,
        track: bool
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    vehicle.is_tracked = track
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)
    return vehicle
