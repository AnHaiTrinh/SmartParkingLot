from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import ParkingLotCreate, ParkingLotUpdate, ParkingLotCreateOut, ParkingLotOut
from ..models.models import ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/api/parking_space_availabilities',
    tags=['ParkingSpaceAvailabilities']
)
