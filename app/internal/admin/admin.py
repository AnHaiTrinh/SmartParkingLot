from fastapi import APIRouter
from app.internal.admin import activity_log, rating_feedback, vehicle, parking_lot, parking_space

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)

router.include_router(activity_log.router)
router.include_router(rating_feedback.router)
router.include_router(vehicle.router)
router.include_router(parking_lot.router)
router.include_router(parking_space.router)
