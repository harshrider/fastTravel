# models.py
from enum import Enum as PyEnum  # Alias Python's Enum to PyEnum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database import Base


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


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    price_A = Column(Float, nullable=False)
    price_B = Column(Float, nullable=False)
    price_C = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)

    # Add other fields as needed


class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    price_A = Column(Float, nullable=False)
    price_B = Column(Float, nullable=False)
    price_C = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)

    # Add other fields as needed


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
