from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, JSON
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from app.configs.db_configs import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

    vehicles = relationship("Vehicle", back_populates="owner")
    ratings_feedbacks = relationship("RatingFeedback", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")


class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    available_spaces = Column(MutableDict.as_mutable(JSON), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

    ratings_feedbacks = relationship("RatingFeedback", back_populates="parking_lot")
    activity_logs = relationship("ActivityLog", back_populates="parking_lot")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, server_default=text("now()"))

    owner = relationship("User", back_populates="vehicles")


class RatingFeedback(Base):
    __tablename__ = "rating_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"))
    rating = Column(Integer, nullable=False)
    feedback = Column(String, nullable=True, server_default=text("NULL"))
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

    user = relationship("User", back_populates="ratings_feedbacks")
    parking_lot = relationship("ParkingLot", back_populates="ratings_feedbacks")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    activity_type = Column(String, nullable=False)
    license_plate = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="activity_logs")
    parking_lot = relationship("ParkingLot", back_populates="activity_logs")
