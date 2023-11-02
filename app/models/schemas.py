from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from ..models.models import VehicleType

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
    updated_at: Optional[datetime]


class UserUpdate(BaseModel):
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str

# ParkingLot
class BaseParkingLot(BaseModel):
    name: str

class ParkingLotCreate(BaseParkingLot):
    address: str

class ParkingLotUpdate(BaseModel):
    name: str
    address: str
    
class ParkingLotCreateOut(BaseModel):
    id: int
    name: str
    address: str
    created_at: datetime

class ParkingLotOut(BaseModel):
    id: int
    name: str
    address: str
    created_at: datetime
    updated_at: Optional[datetime]

# Vehicle
class BaseVehicle(BaseModel):
    license_plate: str
    
class VehicleCreate(BaseVehicle):
    vehicle_type: VehicleType
    owner_id: str
    payment_info: str

class VehicleUpdate(BaseModel):
    license_plate: str
    vehicle_type: VehicleType
    payment_info: str

class VehicleCreateOut(BaseModel):
    id: int
    license_plate: str
    vehicle_type: VehicleType
    owner_id: str
    payment_info: str
    create_at: datetime

class VehicleOut(BaseModel):
    id: int
    license_plate: str
    vehicle_type: VehicleType
    owner_id: str
    payment_info: str
    create_at: datetime
    update_at: Optional[datetime]
