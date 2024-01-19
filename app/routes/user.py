from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

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
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@router.get('/me', response_model=UserOut, status_code=status.HTTP_200_OK)
def get_current_user(current_active_user: CurrentActiveUserDependency):
    return current_active_user


# admin
@router.get('/', response_model=Page[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(
        db: DatabaseDependency,
        current_active_user: CurrentActiveUserDependency,
        show_deleted: bool = Query(default=False),
        username: Optional[str] = Query(default=None)
):
    if not current_active_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    query = db.query(User)
    if not show_deleted:
        query = query.filter(User.is_active == True)
    if username is not None:
        query = query.filter(User.username.ilike(f'{username.lower()}%'))
    return paginate(query)


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
    user.is_superuser = user_update.is_superuser
    user.updated_at = datetime.utcnow()
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
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    db.commit()
    return
