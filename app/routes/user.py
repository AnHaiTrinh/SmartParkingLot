from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..models.schemas import UserCreate, UserCreateOut, UserUpdate, UserOut
from ..models.models import User
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency
from ..utils.password import hash_password

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/', response_model=UserCreateOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DatabaseDependency):
    hashed_password = hash_password(user.password)
    user.password = hashed_password

    try:
        new_user = User(**user.model_dump())
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists')


@router.get('/me', response_model=UserOut, status_code=status.HTTP_200_OK)
def get_current_user(current_user: CurrentActiveUserDependency):
    return current_user

#admin
@router.get('/', response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(db: DatabaseDependency, current_user: CurrentActiveUserDependency):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    users = db.query(User).all()
    return users


@router.get('/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: DatabaseDependency, current_active_user: CurrentActiveUserDependency):
    if current_active_user.id != user_id and not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.put('/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(user_id: int,
                user_update: UserUpdate,
                db: DatabaseDependency,
                current_active_user: CurrentActiveUserDependency):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    elif user.is_superuser == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='There is no permission to change Admin data')
    user.is_superuser = user_update.is_superuser
    db.commit()
    db.refresh(user)
    return user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DatabaseDependency, current_active_user: CurrentActiveUserDependency):
    if current_active_user.id != user_id and not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    elif user.is_superuser == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='There is no permission to delete Admin data')
    user.is_active = False
    user.lock_at = datetime.now()
    db.commit()
    return
