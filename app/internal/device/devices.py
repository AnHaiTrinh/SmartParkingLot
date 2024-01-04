from fastapi import APIRouter
from app.internal.device import camera, sensor

router = APIRouter(
    prefix='/device'
)

router.include_router(camera.router)
router.include_router(sensor.router)
