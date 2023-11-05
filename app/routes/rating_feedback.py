from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from ..models.schemas import RatingFeedbackCreate, RatingFeedbackUpdate, RatingFeedbackCreateOut, RatingFeedbackOut
from ..models.models import RatingFeedback, ParkingLot
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency

router = APIRouter(
    prefix='/ratings_feedbacks',
    tags=['RatingFeedbacks']
)

@router.get('/{parking_lot_id}', response_model=List[RatingFeedbackOut], status_code=status.HTTP_200_OK)
def get_parking_lot_ratings_feedbacks(parking_lot_id: int, db: DatabaseDependency):
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot no found")
    query = db.query(RatingFeedback).join(ParkingLot, ParkingLot.id == parking_lot_id)
    parking_lot_ratings_feedbacks = query.all()
    return parking_lot_ratings_feedbacks

@router.post('/', response_model=RatingFeedbackCreateOut, status_code=status.HTTP_201_CREATED)
def create_ratings_feedbacks(rating_feedback: RatingFeedbackCreate, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    new_rating_feedback = RatingFeedback(**rating_feedback.model_dump())
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == new_rating_feedback.parking_lot_id, ParkingLot.is_active == True).first()
    if not parking_lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot no found")
    new_rating_feedback.user_id = current_active_user.id
    db.add(new_rating_feedback)
    db.commit()
    db.refresh(new_rating_feedback)
    return new_rating_feedback

@router.get('/{rating_feedback_id}', response_model=RatingFeedbackOut, status_code=status.HTTP_200_OK)
def get_rating_feedback_id(rating_feedback_id: int, db: DatabaseDependency):
    rating_feedback = db.query(RatingFeedback).filter(RatingFeedback.id == rating_feedback_id, RatingFeedback.is_active == True).first()
    if not rating_feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating feedback not found')
    return rating_feedback

@router.put('/{rating_feedback_id}', response_model=RatingFeedbackOut, status_code=status.HTTP_200_OK)
def update_rating_feedback(rating_feedback_id: int, update_rating_feedback: RatingFeedbackUpdate, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if not current_active_user.is_superuser and not rating_feedback.user_id == current_active_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    rating_feedback = db.query(RatingFeedback).filter(RatingFeedback.id == rating_feedback_id, RatingFeedback.is_active == True).first()
    if not rating_feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating feedback not found')
    rating_feedback.rating = update_rating_feedback.rating
    rating_feedback.feedback = update_rating_feedback.feedback
    rating_feedback.updated_at = datetime.now()
    db.commit()
    db.refresh(rating_feedback)
    return rating_feedback

@router.delete('/{rating_feedback_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_rating_feedback(rating_feedback_id: int, current_active_user: CurrentActiveUserDependency, db: DatabaseDependency):
    if not current_active_user.is_superuser and not rating_feedback.user_id == current_active_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    rating_feedback = db.query(RatingFeedback).filter(RatingFeedback.id == rating_feedback_id, RatingFeedback.is_active == True).first()
    if not rating_feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating feedback not found')
    rating_feedback.rating = update_rating_feedback.rating
    rating_feedback.feedback = update_rating_feedback.feedback
    rating_feedback.is_active = False
    rating_feedback.deleted_at = datetime.now()
    db.commit()
    return
    
