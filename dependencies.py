from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRoleEnum
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        logger.info("No access_token cookie found.")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.info("No 'sub' in JWT payload.")
            return None
        user = db.query(User).filter(User.username == username).first()
        if user:
            logger.info(f"Authenticated user: {user.username}")
        else:
            logger.info(f"User '{username}' not found in the database.")
        return user
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        return None

def employee_required(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if current_user.role not in [UserRoleEnum.E, UserRoleEnum.S]:  # Allow only employees and super users
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees only. Access denied.")
    return current_user

def superuser_required(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if current_user.role != UserRoleEnum.S:  # Allow only super users
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super users only. Access denied.")
    return current_user
