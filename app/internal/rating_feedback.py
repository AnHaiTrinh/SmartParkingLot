from typing import Optional

from fastapi import APIRouter, status, Query, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func

from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency
from ..models.models import RatingFeedback
from ..models.schemas import RatingFeedbackOut

router = APIRouter()


@router.get('/ratings_feedbacks', response_model=Page[RatingFeedbackOut], status_code=status.HTTP_200_OK)
def get_rating_feedbacks(
        current_active_user: CurrentActiveUserDependency,
        db: DatabaseDependency,
        sort: str = Query(default='desc', regex='^(desc|asc)$'),
        order: str = Query(default='creation', regex='^(creation|rating)$'),
        user_id: Optional[int] = Query(default=None)
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have admin privileges')
    query = db.query(RatingFeedback)
    if user_id is not None:
        query = query.filter(RatingFeedback.user_id == user_id)
    sort_condition = func.coalesce(RatingFeedback.updated_at, RatingFeedback.created_at) if order == 'creation' \
        else RatingFeedback.rating
    order_by = sort_condition.desc() if sort == 'desc' else sort_condition.asc()
    results = paginate(query.order_by(order_by))
    if not results.items:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results
