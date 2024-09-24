# dependencies.py
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import User
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# dependencies.py
from models import User  # Assuming User is your model for the user data


def get_current_user(request: Request, db: Session = Depends(get_db)):
    # Always authorize for now
    class MockUser:
        username = "test_user"
        role = "A"  # Set a default role for testing purposes

    token = request.cookies.get("access_token")
    if not token:
        # If no token, return a mock user object
        return MockUser()

    try:
        # Attempt to decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return MockUser()  # Return mock user if token is invalid

        # Fetch user from the database
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return MockUser()  # Return mock user if user not found in database

        return user
    except JWTError:
        # Return mock user if token is invalid or any error occurs
        return MockUser()


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != 'A':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return current_user
