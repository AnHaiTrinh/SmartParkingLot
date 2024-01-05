from enum import Enum
from uuid import uuid4, UUID

from pydantic import BaseModel, ConfigDict, Field
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


class UserOut(BaseUser):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


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
class ParkingLotBase(BaseModel):
    name: str
    longitude: float
    latitude: float


class ParkingLotCreate(ParkingLotBase):
    pass


class ParkingLotCreateOut(ParkingLotBase):
    id: int


class ParkingLotOut(ParkingLotBase):
    id: int


class ParkingLotUpdate(BaseModel):
    name: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class ParkingLotAdminOut(ParkingLotOut):
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


# Vehicle
class VehicleType(str, Enum):
    car = 'car'
    motorbike = 'motorbike'
    truck = 'truck'


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
    id: int
    created_at: datetime


class VehicleOut(BaseVehicle):
    id: int


class VehicleAdminOut(VehicleOut):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: Optional[datetime] = None
    is_tracked: bool
    owner: Owner


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
    timestamp: datetime
    activity_type: str
    vehicle: VehicleOut


class ActivityLogAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parking_lot: ParkingLotAdminOut
    timestamp: datetime
    activity_type: str
    vehicle: VehicleAdminOut


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


class RatingFeedbackAdminOut(RatingFeedbackOut):
    is_active: bool
    deleted_at: Optional[datetime] = None


class ParkingSpaceBase(BaseModel):
    longitude: int
    latitude: int
    parking_lot_id: int
    vehicle_type: VehicleType


class ParkingSpaceCreate(ParkingSpaceBase):
    pass


class ParkingSpaceCreateOut(ParkingSpaceBase):
    id: int
    created_at: datetime
    state: str


class ParkingSpaceOut(ParkingSpaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    state: str
    vehicle: Optional[VehicleOut] = None


class ParkingSpaceAdminOut(ParkingSpaceOut):
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    parking_lot: ParkingLotAdminOut


# Camera
class CameraBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    parking_lot_id: int


class CameraCreate(CameraBase):
    pass


class CameraCreateOut(CameraBase):
    created_at: datetime
    api_key: str


class CameraOut(CameraBase):
    created_at: datetime
    is_active: bool
    created_at: Optional[datetime] = None


# Sensor
class SensorBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    parking_space_id: int


class SensorCreate(SensorBase):
    pass


class SensorCreateOut(SensorBase):
    created_at: datetime
    api_key: str


class SensorOut(SensorBase):
    created_at: datetime
    is_active: bool
    deleted_at: Optional[datetime] = None
