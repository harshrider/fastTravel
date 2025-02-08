import logging
import os

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Local imports
from database import get_db
from models import Base, User, Tour, Transport  # Updated for SQLAlchemy
from dependencies import get_current_user
from routers import auth, admin, edit_tours, edit_transports, user_management

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(debug=True)

# SQLAlchemy setup
DATABASE_URL = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)  # Create tables from models

# Template and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency for SQLAlchemy sessions
def get_sqlalchemy_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Hybrid database connection (psycopg2 + SQLAlchemy)
def get_hybrid_db():
    # SQLAlchemy session for ORM operations
    orm_db = SessionLocal()

    # Raw psycopg2 connection for SQL operations
    raw_conn = psycopg2.connect(DATABASE_URL)
    raw_cursor = raw_conn.cursor()

    try:
        yield (orm_db, raw_conn, raw_cursor)
    finally:
        raw_cursor.close()
        raw_conn.close()
        orm_db.close()


# Test database connections
try:
    # Test SQLAlchemy connection
    with SessionLocal() as db:
        db.execute("SELECT 1")
        logger.info("SQLAlchemy connection successful!")

    # Test raw psycopg2 connection
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info("Raw psycopg2 connection successful!")

except OperationalError as e:
    logger.error(f"Database connection failed: {str(e)}")
    raise RuntimeError("Database connection failed") from e

# Include routers
# app.include_router(auth.router)
# app.include_router(admin.router)
# app.include_router(edit_tours.router)
# app.include_router(edit_transports.router)
# app.include_router(user_management.router)


# Updated home route using hybrid approach
@app.get("/")
def home(
        request: Request,
        db=Depends(get_hybrid_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    orm_db, raw_conn, raw_cursor = db
    logger.info("Entered home route")

    try:
        # SQLAlchemy ORM query example
        tours = orm_db.query(Tour).all()

        # Raw psycopg2 query example
        raw_cursor.execute("SELECT * FROM transports")
        transports_data = raw_cursor.fetchall()
        transports = [
            Transport(
                id=row[0],
                name=row[1],
                description=row[2],
                price_A=row[3],
                price_B=row[4],
                price_C=row[5],
                start_time=row[6],
                end_time=row[7],
                max_seats=row[8],
                location_url=row[9],
                is_transfer_service=row[10],
                pickup_location=row[11],
                dropoff_location=row[12]
            ) for row in transports_data
        ]

    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tours": tours,
        "transports": transports,
        "user": current_user
    })