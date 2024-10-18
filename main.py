# main.py
import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from routers import auth, admin, tours, transports, cart  # Ensure 'auth' router is included
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
    handlers=[
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

app = FastAPI(debug=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Template and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)      # Authentication routes
app.include_router(admin.router)     # Admin routes
app.include_router(tours.router)     # Tours routes
app.include_router(transports.router) # Transports routes
app.include_router(cart.router)      # Cart routes

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
        # For debugging purposes, include the actual error message
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tours": tours,
        "transports": transports,
        "user": current_user
    })
