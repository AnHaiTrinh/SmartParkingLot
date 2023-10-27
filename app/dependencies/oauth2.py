import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .db_connection import DatabaseDependency
from ..models.models import User
from ..utils.jwt import verify_jwt_token

auth_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_current_user(db: DatabaseDependency, token: str = Depends(auth_scheme)):
    try:
        user_id = verify_jwt_token(token, secret_key=os.getenv('JWT_ACCESS_SECRET_KEY'))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


CurrentUserDependency = Annotated[User, Depends(get_current_user)]
