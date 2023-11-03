from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    longitude: float
    latitude: float
class ParkingLotUpdate(BaseModel):
    name: str
    longitude: float
    latitude: float 
class ParkingLotCreateOut(BaseModel):
    id: int
    name: str
    longitude: float
    latitude: float
    owner_id: int
    created_at: datetime
class ParkingLotOut(BaseModel):
    id: int
    name: str
    longitude: float
    latitude: float
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]




# Vehicle
class BaseVehicle(BaseModel):
    license_plate: str
class VehicleCreate(BaseVehicle):
    vehicle_type: str
class VehicleUpdate(BaseModel):
    license_plate: str
    vehicle_type: str
class VehicleCreateOut(BaseModel):
    id: int
    license_plate: str
    vehicle_type: str
    owner_id: int
    created_at: datetime
class VehicleOut(BaseModel):
    id: int
    license_plate: str
    vehicle_type: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]



#ActivityLog
class ActivityLogCreate(BaseModel):
    activity_type: str
    license_plate: str
    note: str
    user_id: Optional[int]
    packing_lot_id: Optional[int]
class ActivityLogOut(BaseModel):
    activity_type: str
    license_plate: str
    note: str
    timestamp: datetime
    user_id: Optional[int]
    packing_lot_id: Optional[int]