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
    description: Optional[str]
    price_A: Optional[float]
    price_B: Optional[float]
    price_C: Optional[float]
    image_url: Optional[str]

class TourCreate(TourBase):
    pass

class TourResponse(TourBase):
    id: int

    class Config:
        orm_mode = True

# Define schemas for Transport, Availability, etc.
