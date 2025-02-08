import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from routers import auth, admin, edit_tours, edit_transports, user_management
from database import Base, engine, get_db
from models import User, Tour, Transport
from dependencies import get_current_user
from dotenv import load_dotenv
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

# Add this after your database imports
from sqlalchemy import text

# Test database connection
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {str(e)}")

# Load environment variables
load_dotenv()

app = FastAPI(debug=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Template and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(edit_tours.router)
app.include_router(edit_transports.router)
app.include_router(user_management.router)

# Home route
@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    logging.info("Entered home route")
    if current_user:
        logging.info(f"User '{current_user.username}' is accessing the home page.")
    else:
        logging.info("Unauthenticated user is accessing the home page.")
    try:
        tours = db.query(Tour).all()
        transports = db.query(Transport).all()
    except Exception as e:
        logging.error(f"Error querying database: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tours": tours,
        "transports": transports,
        "user": current_user
    })
