# models.py
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, Time, Text
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class UserRoleEnum(enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    E = 'E'
    O = 'O'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), nullable=False)
    credit = Column(Float, default=0.0)

    # Relationships
    #invoices = relationship("Invoice", back_populates="user")
    # Other relationships...

class Tour(Base):
    __tablename__ = 'tours'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price_A = Column(Float)
    price_B = Column(Float)
    price_C = Column(Float)
    image_url = Column(String(255))
    available_time_start = Column(Time)
    available_time_end = Column(Time)
    phone_number = Column(String(50))
    email = Column(String(255))
    location = Column(String(50))  # Adjust to use an Enum if needed
    days = Column(String(255))
    itinerary = Column(Text)
    tags = Column(String(255))
    map = Column(String(255))

    # Relationships
    availability = relationship("TourAvailability", back_populates="tour")

class TourAvailability(Base):
    __tablename__ = 'tour_availability'

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey('tours.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String(50))
    stock = Column(Integer)

    # Relationships
    tour = relationship("Tour", back_populates="availability")

# Define other models (Transport, TransportAvailability, Invoice, etc.)
