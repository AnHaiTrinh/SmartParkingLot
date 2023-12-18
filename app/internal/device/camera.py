from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.models import Camera
from app.models.schemas import CameraCreate, CameraUpdate, CameraOut, CameraCreateOut

router = APIRouter(
    prefix='/cameras'
)


@router.get('/', response_model=Page[CameraOut], status_code=status.HTTP_200_OK)
def get_cameras(
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
def get_camera_by_id(camera_id: int, db: DatabaseDependency, current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='camera not found')
    return camera


@router.post('/', response_model=CameraCreateOut, status_code=status.HTTP_201_CREATED)
def create_camera(
        camera_create: CameraCreate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    camera = Camera(**camera_create.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.put('/{camera_id}', response_model=CameraOut, status_code=status.HTTP_200_OK)
def update_camera(
        camera_id: int,
        camera_update: CameraUpdate,
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='camera not found')
    camera_update_dict = camera_update.model_dump(exclude_unset=True)
    for key, value in camera_update_dict.items():
        setattr(camera, key, value)
    camera.updated_at = datetime.now()
    db.commit()
    db.refresh(camera)
    return camera


@router.delete('/{camera_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(db: DatabaseDependency, camera_id: int, current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Camera not found')
    camera.is_active = False
    camera.deleted_at = datetime.now()
    db.commit()
    return
