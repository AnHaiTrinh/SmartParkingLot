from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from app.configs.db_configs import Base
from enum import Enum

# Định nghĩa kiểu enum cho vehicle_type

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_superuser = Column(Boolean, default=False)
    refresh_token = Column(String, default=None, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_active = Column(Boolean, default=True)
    lock_at = Column(TIMESTAMP, server_default=text("NULL"))

class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True)
    longitude  = Column(Float)
    latitude  = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

class ParkingSpaceAvailability(Base):
    __tablename__ = "parking_space_availability"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    vehicle_type = Column(String)
    available_spaces = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))


class RatingFeedback(Base):
    __tablename__ = "ratings_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    rating = Column(Integer, default=0)
    feedback = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    activity_type = Column(String)
    license_plate = Column(String)
    note = Column(String)
    timestamp = Column(TIMESTAMP, server_default=text("now()"))
    user_id = Column(Integer, ForeignKey("users.id"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))