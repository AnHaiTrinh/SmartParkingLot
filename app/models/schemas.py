from enum import Enum

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# User
class BaseUser(BaseModel):
    username: str


class UserCreate(BaseUser):
    password: str


class UserCreateOut(BaseUser):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserOut(BaseUser):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    is_superuser: bool


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenType(str, Enum):
    access_token = 'access'
    refresh_token = 'refresh'


class TokenData(BaseModel):
    token_type: TokenType
    token: str


# Parking Lot
class AvailableSpaces(BaseModel):
    car: int
    motorbike: int
    bicycle: int


class OptionalAvailableSpaces(BaseModel):
    car: Optional[int] = None
    motorbike: Optional[int] = None
    bicycle: Optional[int] = None


class BaseParkingLot(BaseModel):
    name: str
    longitude: float
    latitude: float
    available_spaces: AvailableSpaces


class ParkingLotCreate(BaseParkingLot):
    pass


class ParkingLotUpdate(BaseModel):
    name: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    available_spaces: Optional[OptionalAvailableSpaces] = None


class ParkingLotCreateOut(BaseParkingLot):
    id: int
    created_at: datetime


class ParkingLotOut(BaseParkingLot):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Vehicle
class Owner(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool


class BaseVehicle(BaseModel):
    license_plate: str
    vehicle_type: str


class VehicleCreate(BaseVehicle):
    pass


class VehicleCreateOut(BaseVehicle):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class VehicleOut(BaseVehicle):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ActivityLog
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class ParkingLot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parking_lot: ParkingLot
    user: User
    timestamp: datetime
    activity_type: str
    license_plate: str


# Rating Feedback
class BaseRatingFeedback(BaseModel):
    rating: int
    feedback: Optional[str] = None


class RatingFeedbackCreate(BaseRatingFeedback):
    pass


class RatingFeedbackUpdate(BaseModel):
    rating: Optional[int]
    feedback: Optional[str]


class RatingFeedbackCreateOut(BaseRatingFeedback):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: User
    parking_lot: ParkingLot
    created_at: datetime


class RatingFeedbackOut(BaseRatingFeedback):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: User
    parking_lot: ParkingLot
    created_at: datetime
    updated_at: Optional[datetime]
