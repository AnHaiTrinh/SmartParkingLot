import os
import datetime
from typing import Union

import redis
from fastapi import HTTPException, status, Depends

from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.redis_connection import RedisDependency, get_redis
from jose import jwt

from ..models.models import User


def create_jwt_token(data: dict, secret_key: str, expiry: dict) -> str:
    to_encode = data.copy()
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(**expiry)
    to_encode.update({"exp": expire_time})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=os.getenv("ALGORITHM"))

    return encoded_jwt


def verify_jwt_token(
        bearer_token: str,
        secret_key: str,
        db: DatabaseDependency,
        redis_client: RedisDependency):
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials",
                              headers={"WWW-Authenticate": "Bearer"})
    state = redis_client.get(bearer_token)
    if state is not None and state.decode('utf8') == 'revoked':
        raise exception
    try:
        payload = jwt.decode(bearer_token, secret_key, algorithms=[os.getenv("ALGORITHM")])
        user_id = payload.get("user_id")
        is_superuser = payload.get("is_superuser")
        if user_id is None or is_superuser is None:
            raise exception
        user = db.query(User).filter(User.id == user_id).first()
        if (not user) or (is_superuser and not user.is_superuser):
            raise exception
        return user
    except Exception as e:
        print(e)
        raise exception
