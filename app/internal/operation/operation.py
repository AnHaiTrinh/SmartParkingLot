from fastapi import APIRouter
from app.internal.operation import parking_space

router = APIRouter(
    prefix='/operation',
    tags=['Operation']
)

router.include_router(parking_space.router)