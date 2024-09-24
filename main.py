# main.py
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from routers import auth, admin, tours, transports
from database import Base, engine, get_db
from models import Tour #, Transport
from dependencies import get_current_user
import os

from database import Base, engine
from models import User, Tour, TourAvailability  # Import your models



app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Template and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(tours.router)
app.include_router(transports.router)

# Home route
@app.get("/")
def home(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tours = db.query(Tour).all()
    #transports = db.query(Transport).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tours": tours,
        "transports": transports,
        "user": 'A'
    })
