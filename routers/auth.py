# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import User, UserRoleEnum
#from schemas import UserCreate
from database import get_db
from fastapi.responses import RedirectResponse
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return None
    return user

@router.post("/login/")
def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False  # Set to True if using HTTPS
    )
    return response

@router.post("/signup/")
def signup(
    response: Response,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: UserRoleEnum = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False  # Set to True if using HTTPS
    )
    return response

@router.get("/logout/")
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
