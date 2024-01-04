from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, UUID
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


class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

    ratings_feedbacks = relationship("RatingFeedback", back_populates="parking_lot")
    parking_spaces = relationship("ParkingSpace", back_populates="parking_lot")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    api_key = Column(String, unique=True, nullable=False, index=True,
                     server_default=text("encode(sha256(random()::text::bytea), 'hex')"))
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

    parking_lot = relationship("ParkingLot")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    api_key = Column(String, unique=True, nullable=False, index=True,
                     server_default=text("encode(sha256(random()::text::bytea), 'hex')"))
    parking_space_id = Column(Integer, ForeignKey("parking_spaces.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))

    parking_space = relationship("ParkingSpace", back_populates="sensor")


class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, server_default=text("NULL"))
    vehicle_type = Column(String, nullable=False)
    state = Column(String, nullable=False, server_default=text("'free'"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True, unique=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"))

    sensor = relationship("Sensor", uselist=False, back_populates="parking_space")
    vehicle = relationship("Vehicle")
    parking_lot = relationship("ParkingLot", back_populates="parking_spaces")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String, nullable=False)
    is_tracked = Column(Boolean, default=False)
    updated_at = Column(TIMESTAMP, server_default=text("NULL"))
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

    user = relationship("User")
    parking_lot = relationship("ParkingLot")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    activity_type = Column(String, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False)

    vehicle = relationship("Vehicle")
    parking_lot = relationship("ParkingLot")
