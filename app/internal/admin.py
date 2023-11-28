from fastapi import APIRouter
from app.internal import activity_log, rating_feedback, vehicle

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)

router.include_router(activity_log.router)
router.include_router(rating_feedback.router)
router.include_router(vehicle.router)