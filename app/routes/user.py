from fastapi import APIRouter, Depends, HTTPException, status
from ..models.schemas import UserCreate, UserOut
from ..models.models import User
from ..dependencies.db_connection import DatabaseDependency
from ..utils.hash_password import hash

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DatabaseDependency):
    hashed_password = hash(user.password)
    user.password = hashed_password

    new_user = User(**user.model_dump(exclude_unset=True))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
