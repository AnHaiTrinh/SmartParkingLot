from enum import Enum
from uuid import uuid4, UUID

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
class VehicleCapacity(BaseModel):
    total_visit: int = 0
    vehicle_in_count: int = 0
    vehicle_out_count: int = 0
    current_capacity: int = 0
    max_capacity: int = 0


class ParkingLotSpace(BaseModel):
    total: VehicleCapacity
    car: VehicleCapacity
    motorbike: VehicleCapacity
    bicycle: VehicleCapacity


class ParkingLotRatingDetail(BaseModel):
    one_star: int = 0
    two_star: int = 0
    three_star: int = 0
    four_star: int = 0
    five_star: int = 0


class ParkingLotRating(BaseModel):
    total: int = 0
    average: float = 0.0
    detail: ParkingLotRatingDetail


class BaseParkingLot(BaseModel):
    name: str
    longitude: float
    latitude: float


class ParkingLotCreate(BaseParkingLot):
    pass


class ParkingLotUpdate(BaseModel):
    name: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class ParkingLotCreateOut(BaseParkingLot):
    id: int
    created_at: datetime


class ParkingLotOut(BaseParkingLot):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    parking_space: ParkingLotSpace
    rating: ParkingLotRating


class ParkingLotAdminOut(ParkingLotOut):
    is_active: bool
    deleted_at: Optional[datetime] = None


# Vehicle
class Owner(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool


class VehicleType(str, Enum):
    car = 'car'
    motorbike = 'motorbike'
    bicycle = 'bicycle'


class BaseVehicle(BaseModel):
    license_plate: str
    vehicle_type: VehicleType


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


class VehicleAdminOut(VehicleOut):
    model_config = ConfigDict(from_attributes=True)

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


# Parking Space
class BaseParkingSpace(BaseModel):
    longitude: float
    latitude: float
    parking_lot_id: int
    vehicle_type: VehicleType


class ParkingSpaceCreate(BaseParkingSpace):
    pass


class ParkingSpaceCreateOut(BaseParkingSpace):
    id: int
    is_active: bool
    created_at: datetime


class ParkingSpaceOut(BaseParkingSpace):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool

    parking_lot: ParkingLotOut


class ParkingSpaceUpdate(BaseModel):
    longitude: Optional[float]
    latitude: Optional[float]
    parking_lot_id: Optional[int]


class ParkingSpaceAdminOut(ParkingSpaceOut):
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    vehicle: Optional[VehicleOut] = None


# Sensor
class BaseSensor(BaseModel):
    id: UUID = uuid4()
    parking_space_id: int


class SensorCreate(BaseSensor):
    pass


class SensorCreateOut(BaseSensor):
    api_key: str
    created_at: datetime
    is_active: bool


class SensorOut(BaseSensor):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    is_active: bool
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    parking_space: ParkingSpaceOut


class SensorUpdate(BaseModel):
    parking_space_id: Optional[int]


# Camera
class BaseCamera(BaseModel):
    id: UUID = uuid4()
    parking_lot_id: int


class CameraCreate(BaseCamera):
    pass


class CameraCreateOut(BaseCamera):
    api_key: str
    created_at: datetime
    is_active: bool


class CameraOut(BaseCamera):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    is_active: bool
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    parking_lot: ParkingLotOut


class CameraUpdate(BaseModel):
    parking_lot_id: Optional[int]
