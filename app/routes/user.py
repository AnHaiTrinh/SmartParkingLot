from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..models.schemas import UserCreate, UserOut
from ..models.models import User
from ..dependencies.db_connection import DatabaseDependency
from ..utils.password import hash_password

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
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

