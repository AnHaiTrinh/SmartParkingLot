from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from app.configs.db_configs import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    refresh_token = Column(String, default=None, nullable=True)

class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(String)
    total_spaces = Column(Integer)
    available_spaces = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    payment_info = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

    #owner = relationship("User", back_populates="vehicles")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    start_time = Column(TIMESTAMP, server_default=text("now()"))
    end_time = Column(TIMESTAMP)
    parking_fee = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

class RatingFeedback(Base):
    __tablename__ = "ratings_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    rating = Column(Integer)
    feedback = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    activity_type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    timestamp = Column(TIMESTAMP, server_default=text("now()"))