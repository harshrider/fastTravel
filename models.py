from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Enum as SQLAlchemyEnum, Date, Time, Boolean
from sqlalchemy.orm import relationship
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

class UserRoleEnum(PyEnum):
    A = "A"  # Admin
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

    # Relationships
    carts = relationship("Cart", back_populates="user")

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
    max_tickets = Column(Integer, nullable=False)  # Max tickets per day
    image_url = Column(String, nullable=True)  # Legacy field if needed

    # Relationships
    tags = relationship("Tag", secondary=tour_tag_association, backref="tours")
    images = relationship("Image", primaryjoin="Tour.id == Image.tour_id")
    availabilities = relationship("TourAvailability", back_populates="tour")

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
    max_seats = Column(Integer, nullable=False)  # Max seats per day
    image_url = Column(String, nullable=True)  # Legacy field if needed

    # Relationships
    tags = relationship("Tag", secondary=transport_tag_association, backref="transports")
    images = relationship("Image", primaryjoin="Transport.id == Image.transport_id")
    availabilities = relationship("TransportAvailability", back_populates="transport")

class TourAvailability(Base):
    __tablename__ = "tour_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    date = Column(Date, nullable=False)
    available_tickets = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationships
    tour = relationship("Tour", back_populates="availabilities")

class TransportAvailability(Base):
    __tablename__ = "transport_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=False)
    date = Column(Date, nullable=False)
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
    quantity = Column(Integer, default=1, nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    tour = relationship("Tour")
    transport = relationship("Transport")
