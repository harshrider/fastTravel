from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Table,
    Enum as SQLAlchemyEnum, Date, Time, Boolean, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

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

tour_transport_association = Table(
    "tour_transport_association", Base.metadata,
    Column("tour_id", Integer, ForeignKey("tours.id"), primary_key=True),
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
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLAlchemyEnum(UserRoleEnum), default=UserRoleEnum.A, nullable=False)
    credit = Column(Float, default=0.0, nullable=False)

    # Relationships
    carts = relationship("Cart", back_populates="user")
    bookings = relationship("Booking", back_populates="user")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)

    # Relationships
    tour = relationship("Tour", back_populates="images")
    transport = relationship("Transport", back_populates="images")
    package = relationship("Package", back_populates="images")

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    time = Column(Time, nullable=False)
    description = Column(String(500), nullable=False)

    # Relationships
    package = relationship("Package", back_populates="itineraries")
    tour = relationship("Tour", back_populates="itineraries")

class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(String(1000), nullable=True)
    price_A = Column(Float, nullable=False, default=None)
    price_B = Column(Float, nullable=False, default=None)
    price_C = Column(Float, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_tickets = Column(Integer, nullable=False, default=1000)
    location_url = Column(String(255), nullable=True)
    cancellation_policy = Column(String(1000), nullable=True, default="No cancellation policy specified.")
    refund_policy = Column(String(1000), nullable=True, default="No refund policy specified.")
    rate_a = Column(String(1000), nullable=True, default="Standard rate applies.")
    rate_b = Column(String(1000), nullable=True, default="Standard rate applies.")
    rate_c = Column(String(1000), nullable=True, default="Standard rate applies.")

    # Relationships
    tags = relationship("Tag", secondary=tour_tag_association, backref="tours")
    images = relationship("Image", primaryjoin="Tour.id == Image.tour_id", back_populates="tour")
    availabilities = relationship("TourAvailability", back_populates="tour", cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="tour", order_by="Itinerary.time")
    cart_items = relationship("CartItem", back_populates="tour")
    bookings = relationship("Booking", back_populates="tour")
    transports = relationship("Transport", secondary=tour_transport_association, back_populates="tours")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default values for price_A and price_B if they are None
        if self.price_A is None:
            self.price_A = self.price_B
        if self.price_B is None:
            self.price_B = self.price_C

class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(String(1000), nullable=False)
    price_A = Column(Float, nullable=False)
    price_B = Column(Float, nullable=False)
    price_C = Column(Float, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_seats = Column(Integer, nullable=False)
    location_url = Column(String(255), nullable=True)
    is_transfer_service = Column(Boolean, default=False)  # Indicates if it's a transfer service


    # Pickup and Drop-off locations
    pickup_location = Column(String(255), nullable=True)
    dropoff_location = Column(String(255), nullable=True)

    # Relationships
    tags = relationship("Tag", secondary=transport_tag_association, backref="transports")
    images = relationship("Image", primaryjoin="Transport.id == Image.transport_id", back_populates="transport")
    availabilities = relationship("TransportAvailability", back_populates="transport", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="transport")
    bookings = relationship("Booking", back_populates="transport")
    tours = relationship("Tour", secondary=tour_transport_association, back_populates="transports")


class TourAvailability(Base):
    __tablename__ = "tour_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    available_tickets = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    price_modifier = Column(Float, default=0.0)  # Add this line

    # Relationships
    tour = relationship("Tour", back_populates="availabilities")

class TransportAvailability(Base):
    __tablename__ = "transport_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    available_seats = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationships
    transport = relationship("Transport", back_populates="availabilities")

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    price_A = Column(Float, nullable=False)
    price_B = Column(Float, nullable=False)
    price_C = Column(Float, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    tours = relationship("Tour", secondary=package_tour_association, backref="packages")
    transports = relationship("Transport", secondary=package_transport_association, backref="packages")
    images = relationship("Image", back_populates="package")
    itineraries = relationship("Itinerary", back_populates="package", order_by="Itinerary.time")
    cart_items = relationship("CartItem", back_populates="package")
    bookings = relationship("Booking", back_populates="package")
    creator = relationship("User")

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    tour = relationship("Tour", back_populates="cart_items")
    transport = relationship("Transport", back_populates="cart_items")
    package = relationship("Package", back_populates="cart_items")

class BookingStatusEnum(PyEnum):
    CONFIRMED = "Confirmed"
    PENDING = "Pending"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLAlchemyEnum(BookingStatusEnum), default=BookingStatusEnum.CONFIRMED, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")
    transport = relationship("Transport", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")

from datetime import timedelta

def generate_time_slots(start_time, end_time, interval_minutes=60):
    """Utility to generate time slots between start and end times."""
    slots = []
    current_time = datetime.combine(datetime.today(), start_time)
    end_time_dt = datetime.combine(datetime.today(), end_time)

    while current_time <= end_time_dt - timedelta(minutes=interval_minutes):
        slots.append(current_time.time())
        current_time += timedelta(minutes=interval_minutes)
    return slots

def create_tour_availability(tour, start_date, end_date, db):
    """Creates availability for a tour from start_date to end_date."""
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
    """Creates availability for a transport from start_date to end_date."""
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
