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
    created_at: datetime
class ParkingLotOut(BaseModel):
    id: int
    name: str
    longitude: float
    latitude: float
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
    parking_lot_id: int
    activity_type: str
    license_plate: str
class ActivityLogOut(BaseModel):
    id: int
    parking_lot_id: int
    activity_type: str
    license_plate: str
    timestamp: datetime



#ParkingSpaceAvailability
class ParkingSpaceAvailabilityCreate(BaseModel):
    parking_lot_id: int
    vehicle_type: str
    available_spaces: int
class ParkingSpaceAvailabilityUpdate(BaseModel):
    available_spaces: int
class ParkingSpaceAvailabilityCreateOut(BaseModel):
    id: int
    parking_lot_id: int
    vehicle_type: str
    available_spaces: int
    created_at: datetime
class ParkingSpaceAvailabilityOut(BaseModel):
    id: int
    parking_lot_id: int
    vehicle_type: str
    available_spaces: int
    created_at: datetime
    updated_at: Optional[datetime]



#RatingFeedback
class RatingFeedbackCreate(BaseModel):
    parking_lot_id: int
    rating: int
    feedback: str
class RatingFeedbackUpdate(BaseModel):
    rating: int
    feedback: str
class RatingFeedbackCreateOut(BaseModel):
    id: int
    rating: int
    feedback: str
    created_at: datetime
class RatingFeedbackOut(BaseModel):
    id: int
    rating: int
    feedback: str
    created_at: datetime
    updated_at: Optional[datetime]