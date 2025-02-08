from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from database import get_db
from models import User, UserRoleEnum
import os
import logging
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(
    db: Session = Depends(SessionLocal),
    token: str = Depends(oauth2_scheme)
):
    # Your authentication logic using SQLAlchemy session
    # ...
# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


# def get_current_user(request: Request, db=Depends(get_db)) -> Optional[User]:
#     token = request.cookies.get("access_token")
#     if not token:
#         logger.info("No access_token cookie found.")
#         return None
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             logger.info("No 'sub' in JWT payload.")
#             return None
#
#         # Execute raw SQL query using psycopg2
#         with db.cursor() as cursor:
#             cursor.execute(
#                 "SELECT id, username, email, password_hash, role, credit FROM users WHERE username = %s",
#                 (username,)
#             )
#             user_data = cursor.fetchone()
#
#         if user_data:
#             user = User(
#                 id=user_data[0],
#                 username=user_data[1],
#                 email=user_data[2],
#                 password_hash=user_data[3],
#                 role=UserRoleEnum(user_data[4]),
#                 credit=user_data[5]
#             )
#             logger.info(f"Authenticated user: {user.username}")
#             return user
#         else:
#             logger.info(f"User '{username}' not found in the database.")
#             return None
#     except JWTError as e:
#         logger.error(f"JWT decoding error: {e}")
#         return None


def employee_required(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if current_user.role not in [UserRoleEnum.E, UserRoleEnum.S]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees only. Access denied.")
    return current_user


def superuser_required(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if current_user.role != UserRoleEnum.S:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super users only. Access denied.")
    return current_user