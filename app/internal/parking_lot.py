from typing import Optional

from fastapi import APIRouter, status, Query, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency
from ..models.schemas import ParkingLotAdminOut
from ..models.models import ParkingLot

router = APIRouter()


@router.get('/parking_lots', response_model=Page[ParkingLotAdminOut], status_code=status.HTTP_200_OK)
def get_all_parking_lots(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: Optional[bool] = Query(default=False),
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
