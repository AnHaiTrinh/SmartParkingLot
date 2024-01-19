from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import Camera
from app.models.schemas import CameraOut, CameraCreateOut, CameraCreate

router = APIRouter(
    prefix='/cameras',
    tags=['Cameras']
)


@router.get('/', response_model=Page[CameraOut], status_code=status.HTTP_200_OK)
def get_all_cameras(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
        parking_lot_id: Optional[int] = Query(default=None),
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    query = db.query(Camera)
    if not show_deleted:
        query = query.filter(Camera.is_active == True)
    if parking_lot_id is not None:
        query = query.filter(Camera.parking_lot_id == parking_lot_id)
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.get('/{camera_id}', response_model=CameraOut, status_code=status.HTTP_200_OK)
def get_camera_by_id(
        camera_id: UUID,
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Camera not found')
    return camera


@router.post('/', response_model=CameraCreateOut, status_code=status.HTTP_201_CREATED)
def create_camera(
        camera_create: CameraCreate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    new_camera = Camera(**camera_create.model_dump())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera


@router.delete('/{camera_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
        camera_id: UUID,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Camera not found')
    camera.is_active = False
    camera.deleted_at = datetime.utcnow()
    db.commit()
    return
