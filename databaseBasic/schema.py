# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum


class UserRoleEnum(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    E = 'E'
    O = 'O'


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRoleEnum


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class TourBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_A: Optional[float] = None
    price_B: Optional[float] = None
    price_C: Optional[float] = None
    image_url: Optional[str] = None


class TourCreate(TourBase):
    pass


class TourResponse(TourBase):
    id: int

    class Config:
        orm_mode = True


class TransportBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_A: Optional[float] = None
    price_B: Optional[float] = None
    price_C: Optional[float] = None
    image_url: Optional[str] = None


class TransportCreate(TransportBase):
    pass


class TransportResponse(TransportBase):
    id: int

    class Config:
        orm_mode = True


class CartItemBase(BaseModel):
    tour_id: Optional[int] = None
    transport_id: Optional[int] = None
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(CartItemBase):
    id: int
    cart_id: int

    class Config:
        orm_mode = True


class CartBase(BaseModel):
    user_id: int


class CartCreate(CartBase):
    pass


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = []

    class Config:
        orm_mode = True
