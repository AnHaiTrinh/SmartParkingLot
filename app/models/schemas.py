from pydantic import BaseModel
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


class UserUpdate(BaseModel):
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str

class ChangeUserPasswordDto:
    old_password: str
    new_password: str
    retype_password: str