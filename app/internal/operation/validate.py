# from fastapi import APIRouter, status, HTTPException
#
# from app.dependencies.db_connection import DatabaseDependency
# from app.dependencies.devices import CameraAuthDependency
# from app.models.models import Camera
# from app.models.schemas import ValidationOut, ValidationIn, ValidationInResponse, ValidationOutResponse
#
# router = APIRouter(
#     prefix='/validate',
#     tags=['Validate']
# )
#
#
# @router.post('/in', response_model=ValidationInResponse, status_code=status.HTTP_200_OK)
# def validate_vehicle_in(
#     db: DatabaseDependency,
#     validate_in: ValidationIn,
# ):
#     pass
#
#
# @router.post('/out', response_model=ValidationOutResponse, status_code=status.HTTP_200_OK)
# def validate_vehicle_out(
#     db: DatabaseDependency,
#     validate_out: ValidationOut,
# ):
#     pass
