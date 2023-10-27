from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BaseUser(BaseModel):
    username: str


class UserCreate(BaseUser):
    password: str


class UserOut(BaseUser):
    id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
