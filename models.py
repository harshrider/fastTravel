from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Table,
    Enum as SQLAlchemyEnum, Date, Time, Boolean, DateTime
)
from sqlalchemy.orm import relationship

from database import Base
# Utility functions
from datetime import datetime, timedelta

# Association tables for many-to-many relationships
tour_tag_association = Table(
    "tour_tag_association", Base.metadata,
    Column("tour_id", Integer, ForeignKey("tours.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

transport_tag_association = Table(
    "transport_tag_association", Base.metadata,
    Column("transport_id", Integer, ForeignKey("transports.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

# Association tables for many-to-many relationships between packages and tours/transports
package_tour_association = Table(
    "package_tour_association", Base.metadata,
    Column("package_id", Integer, ForeignKey("packages.id"), primary_key=True),
    Column("tour_id", Integer, ForeignKey("tours.id"), primary_key=True)
)

package_transport_association = Table(
    "package_transport_association", Base.metadata,
    Column("package_id", Integer, ForeignKey("packages.id"), primary_key=True),
    Column("transport_id", Integer, ForeignKey("transports.id"), primary_key=True)
)

class UserRoleEnum(PyEnum):
    S = "S"  # Superuser
    A = "A"  # AStar Customer
    B = "B"  # Business
    C = "C"  # Customer
    E = "E"  # Employee
    O = "O"  # Other

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRoleEnum), default=UserRoleEnum.C, nullable=False)
    credit = Column(Float, default=0.0, nullable=False)  # New field for user's credit

    # Relationships
    carts = relationship("Cart", back_populates="user")
    bookings = relationship("Booking", back_populates="user")  # New relationship

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)

    # Relationships
    tour = relationship("Tour", back_populates="images")
    transport = relationship("Transport", back_populates="images")
    package = relationship("Package", back_populates="images")

class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    price_A = Column(Float, nullable=False)
    price_B = Column(Float, nullable=False)
    price_C = Column(Float, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_tickets = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    location_url = Column(String, nullable=True)

    # Relationships
    tags = relationship("Tag", secondary=tour_tag_association, backref="tours")
    images = relationship("Image", primaryjoin="Tour.id == Image.tour_id", back_populates="tour")
    availabilities = relationship("TourAvailability", back_populates="tour", cascade="all, delete-orphan")

class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    price_A = Column(Float, nullable=False)
    price_B = Column(Float, nullable=False)
    price_C = Column(Float, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_seats = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    location_url = Column(String, nullable=True)

    # Relationships
    tags = relationship("Tag", secondary=transport_tag_association, backref="transports")
    images = relationship("Image", primaryjoin="Transport.id == Image.transport_id", back_populates="transport")
    availabilities = relationship("TransportAvailability", back_populates="transport", cascade="all, delete-orphan")


class TourAvailability(Base):
    __tablename__ = "tour_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)  # Field for time slots
    available_tickets = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationships
    tour = relationship("Tour", back_populates="availabilities")

class TransportAvailability(Base):
    __tablename__ = "transport_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)  # Field for time slots
    available_seats = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationships
    transport = relationship("Transport", back_populates="availabilities")

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    date = Column(Date, nullable=False)  # New field for booking date
    time = Column(Time, nullable=False)  # New field for booking time
    quantity = Column(Integer, default=1, nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    tour = relationship("Tour")
    transport = relationship("Transport")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="Confirmed", nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    tour = relationship("Tour")
    transport = relationship("Transport")

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    tours = relationship("Tour", secondary=package_tour_association, backref="packages")
    transports = relationship("Transport", secondary=package_transport_association, backref="packages")
    images = relationship("Image", back_populates="package")
    creator = relationship("User")


def generate_time_slots(start_time, end_time, interval_minutes=60):
    slots = []
    current_time = datetime.combine(datetime.today(), start_time)
    end_time_dt = datetime.combine(datetime.today(), end_time)

    while current_time <= end_time_dt - timedelta(minutes=interval_minutes):
        slots.append(current_time.time())
        current_time += timedelta(minutes=interval_minutes)
    return slots

def create_tour_availability(tour, start_date, end_date, db):
    date = start_date
    while date <= end_date:
        time_slots = generate_time_slots(tour.start_time, tour.end_time)
        for time_slot in time_slots:
            availability = TourAvailability(
                tour_id=tour.id,
                date=date,
                time=time_slot,
                available_tickets=tour.max_tickets,
                is_available=True
            )
            db.add(availability)
        date += timedelta(days=1)
    db.commit()

def create_transport_availability(transport, start_date, end_date, db):
    date = start_date
    while date <= end_date:
        time_slots = generate_time_slots(transport.start_time, transport.end_time)
        for time_slot in time_slots:
            availability = TransportAvailability(
                transport_id=transport.id,
                date=date,
                time=time_slot,
                available_seats=transport.max_seats,
                is_available=True
            )
            db.add(availability)
        date += timedelta(days=1)
    db.commit()
