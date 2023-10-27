import os
import datetime

from fastapi import HTTPException, status
from jose import jwt


def create_jwt_token(data: dict, secret_key: str, expiry: dict) -> str:
    to_encode = data.copy()
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(**expiry)
    to_encode.update({"exp": expire_time})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=os.getenv("ALGORITHM"))

    return encoded_jwt


def verify_jwt_token(bearer_token: str, secret_key: str):
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(bearer_token, secret_key, algorithms=[os.getenv("ALGORITHM")])
        user_id = payload.get("user_id")
        if user_id is None:
            raise exception
        return user_id
    except Exception:
        raise exception
