from datetime import datetime
from typing import Optional

from fastapi import APIRouter, status, Query, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies.db_connection import DatabaseDependency
from app.dependencies.oauth2 import CurrentActiveUserDependency
from app.models.schemas import ParkingLotAdminOut, ParkingLotSpace
from app.models.models import ParkingLot

router = APIRouter(prefix='/parking_lots')


@router.get('/', response_model=Page[ParkingLotAdminOut], status_code=status.HTTP_200_OK)
def get_all_parking_lots(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    query = db.query(ParkingLot)
    if not show_deleted:
        query = query.filter(ParkingLot.is_active == True)
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


@router.get('/spaces', response_model=ParkingLotSpace, status_code=status.HTTP_200_OK)
def get_all_parking_lot_spaces(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        parking_lot_id: Optional[int] = Query(default=None),
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    if parking_lot_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot filter by both parking_lot_id and parking_space_id'
        )
    query = db.query(ParkingLot)
    if parking_lot_id is not None:
        query = query.filter(ParkingLot.id == parking_lot_id)
    results = paginate(query)
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results


# @router.get('/{parking_lot_id}/spaces', response_model=ParkingLotSpace, status_code=status.HTTP_200_OK)
# def get_parking_lot_spaces(
#         parking_lot_id: int,
#         timestamp: int = Query(default_factory=lambda: int(datetime.timestamp()), ge=0),
# ):
#     timestamp = datetime.fromtimestamp(fromtime)
#
#
# @router.get('/{parking_lot_id}/ratings', response_model=ParkingLotRating, status_code=status.HTTP_200_OK)
# def get_parking_lot_ratings(
#     parking_lot_id: int,
# ):
#     pass
