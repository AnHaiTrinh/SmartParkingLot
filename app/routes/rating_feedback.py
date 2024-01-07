from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func

from ..models.schemas import RatingFeedbackCreate, RatingFeedbackUpdate, RatingFeedbackCreateOut, RatingFeedbackOut
from ..models.models import RatingFeedback, ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/parking-lots/{parking_lot_id}/rating-feedbacks',
    tags=['RatingFeedbacks']
)


@router.get('/', response_model=Page[RatingFeedbackOut], status_code=status.HTTP_200_OK)
def get_parking_lot_ratings_feedbacks(
        parking_lot_id: int,
        db: DatabaseDependency,
        sort: str = Query(default='desc', regex='^(desc|asc)$'),
        order: str = Query(default='creation', regex='^(creation|rating)$')
):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot no found")
    sort_condition = func.coalesce(RatingFeedback.updated_at, RatingFeedback.created_at) if order == 'creation' \
        else RatingFeedback.rating
    order_by = sort_condition.desc() if sort == 'desc' else sort_condition.asc()
    return paginate(db.query(RatingFeedback)
                    .filter(RatingFeedback.parking_lot_id == parking_lot_id)
                    .order_by(order_by))


@router.post('/', response_model=RatingFeedbackCreateOut, status_code=status.HTTP_201_CREATED)
def create_ratings_feedbacks(parking_lot_id: int,
                             rating_feedback: RatingFeedbackCreate,
                             current_active_user: CurrentActiveUserDependency,
                             db: DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id,
                                              ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")

    new_rating_feedback = RatingFeedback(**rating_feedback.model_dump(exclude_unset=True))
    new_rating_feedback.parking_lot_id = parking_lot_id
    new_rating_feedback.user = current_active_user
    db.add(new_rating_feedback)
    db.commit()
    db.refresh(new_rating_feedback)
    return new_rating_feedback


@router.get('/{rating_feedback_id}', response_model=RatingFeedbackOut, status_code=status.HTTP_200_OK)
def get_rating_feedback_by_id(parking_lot_id: int, rating_feedback_id: int, db: DatabaseDependency):
    rating_feedback = db.query(RatingFeedback).filter(RatingFeedback.id == rating_feedback_id,
                                                      RatingFeedback.is_active == True).first()
    if (not rating_feedback) or rating_feedback.parking_lot_id != parking_lot_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating feedback not found')
    return rating_feedback


@router.put('/{rating_feedback_id}', response_model=RatingFeedbackOut, status_code=status.HTTP_200_OK)
def update_rating_feedback(parking_lot_id: int,
                           rating_feedback_id: int,
                           rating_feedback_update: RatingFeedbackUpdate,
                           current_active_user: CurrentActiveUserDependency,
                           db: DatabaseDependency):
    rating_feedback = db.query(RatingFeedback).filter(RatingFeedback.id == rating_feedback_id,
                                                      RatingFeedback.is_active == True).first()
    if (not rating_feedback) or rating_feedback.parking_lot_id != parking_lot_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating feedback not found')
    if rating_feedback.user_id != current_active_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    rating_feedback_update_dict = rating_feedback_update.model_dump(exclude_unset=True)
    for key, value in rating_feedback_update_dict.items():
        setattr(rating_feedback, key, value)
    rating_feedback.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rating_feedback)
    return rating_feedback


@router.delete('/{rating_feedback_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_rating_feedback(parking_lot_id: int,
                           rating_feedback_id: int,
                           current_active_user: CurrentActiveUserDependency,
                           db: DatabaseDependency):
    rating_feedback = db.query(RatingFeedback).filter(RatingFeedback.id == rating_feedback_id,
                                                      RatingFeedback.is_active == True).first()
    if (not rating_feedback) or rating_feedback.parking_lot_id != parking_lot_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating feedback not found')
    if rating_feedback.user_id != current_active_user.id and not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    rating_feedback.is_active = False
    rating_feedback.deleted_at = datetime.utcnow()
    db.commit()
    return
