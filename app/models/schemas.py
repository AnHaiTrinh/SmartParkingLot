from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BaseUser(BaseModel):
    username: str


class UserCreate(BaseUser):
    password: str


class UserOut(BaseUser):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime


class PasswordUpdate(BaseModel):
    password: str


class UserUpdate(BaseModel):
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str
