import os
from typing import Annotated, Union

from fastapi import APIRouter, HTTPException, Depends, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from ..models.schemas import Token, TokenData
from ..models.models import User
from ..dependencies.db_connection import DatabaseDependency
from ..dependencies.oauth2 import CurrentActiveUserDependency
from ..dependencies.redis_connection import RedisDependency
from ..utils.password import verify_password, hash_password
from ..utils.jwt import create_jwt_token, verify_jwt_token

router = APIRouter(
    tags=['Auth']
)


@router.post('/login', response_model=Token)
def login(response: Response, db: DatabaseDependency,
          redis_client: RedisDependency,
          user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')

    access_token = create_jwt_token(
        data={
            'user_id': user.id,
            'is_superuser': user.is_superuser
        },
        secret_key=os.getenv('JWT_ACCESS_SECRET_KEY'),
        expiry={'minutes': int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))}
    )

    refresh_token = create_jwt_token(
        data={
            'user_id': user.id
        },
        secret_key=os.getenv('JWT_REFRESH_SECRET_KEY'),
        expiry={'days': int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))}
    )
    redis_client.set(refresh_token, user.id, ex=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')) * 60)

    response.set_cookie(key='jwt', value=refresh_token, httponly=True, secure=True, samesite='none',
                        max_age=24 * 60 * 60)
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@router.get("/refresh", response_model=Token)
def refresh_access_token(redis_client: RedisDependency,
                         db: DatabaseDependency,
                         jwt: Annotated[Union[str, None], Cookie()] = None):
    if jwt is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Refresh token not found')
    user_id = redis_client.get(jwt)
    if user_id is None or user_id.decode('utf8') == 'revoked':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    try:
        user_id = int(user_id.decode('utf8'))
        user = verify_jwt_token(jwt, secret_key=os.getenv('JWT_REFRESH_SECRET_KEY'), db=db, redis_client=redis_client)
        if user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials')
        user = db.query(User).filter(User.id == user_id).first()
        access_token = create_jwt_token(
            data={
                'user_id': user_id,
                'is_superuser': user.is_superuser
            },
            secret_key=os.getenv('JWT_ACCESS_SECRET_KEY'),
            expiry={'minutes': int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))}
        )
        return {
            'access_token': access_token,
            'token_type': 'bearer'
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials')


@router.post('/change-password', status_code=status.HTTP_200_OK)
def change_password(db: DatabaseDependency, current_active_user: CurrentActiveUserDependency, new_password: str):
    hashed_password = hash_password(new_password)
    current_active_user.password = hashed_password
    db.commit()
    return {
        'message': 'Password changed successfully'
    }


@router.post('/revoke-token', status_code=status.HTTP_204_NO_CONTENT)
def revoke_token(token_data: TokenData, redis_client: RedisDependency):
    if token_data.token_type == 'access':
        redis_client.set(token_data.token, value='revoked', ex=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')) * 60)
    else:
        redis_client.set(name=token_data.token, value='revoked',
                         ex=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')) * 24 * 60 * 60)
