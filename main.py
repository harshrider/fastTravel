import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from dotenv import load_dotenv
from psycopg2 import OperationalError

# Local imports
from database import get_db
from models import User, Tour, Transport
from dependencies import get_current_user
from routers import auth, admin, edit_tours, edit_transports, user_management

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

# SQL statements to create tables (corrected order)
CREATE_TABLES_SQL = """
-- Create enum types first
CREATE TYPE IF NOT EXISTS user_role_enum AS ENUM ('S', 'A', 'B', 'C', 'E', 'O');
CREATE TYPE IF NOT EXISTS booking_status_enum AS ENUM ('Confirmed', 'Pending', 'Cancelled', 'Completed');

-- Create independent tables first
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'A',
    credit DECIMAL(10, 2) DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS tours (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price_A DECIMAL(10, 2) NOT NULL,
    price_B DECIMAL(10, 2) NOT NULL,
    price_C DECIMAL(10, 2) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_tickets INT NOT NULL,
    location_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price_A DECIMAL(10, 2) NOT NULL,
    price_B DECIMAL(10, 2) NOT NULL,
    price_C DECIMAL(10, 2) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_seats INT NOT NULL,
    location_url TEXT NOT NULL,
    is_transfer_service BOOLEAN DEFAULT FALSE,
    pickup_location TEXT,
    dropoff_location TEXT
);

CREATE TABLE IF NOT EXISTS packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price_A DECIMAL(10, 2) NOT NULL,
    price_B DECIMAL(10, 2) NOT NULL,
    price_C DECIMAL(10, 2) NOT NULL,
    created_by INT REFERENCES users(id) ON DELETE SET NULL
);

-- Create dependent tables
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    tour_id INT REFERENCES tours(id) ON DELETE CASCADE,
    transport_id INT REFERENCES transports(id) ON DELETE CASCADE,
    package_id INT REFERENCES packages(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    package_id INT REFERENCES packages(id) ON DELETE CASCADE,
    tour_id INT REFERENCES tours(id) ON DELETE CASCADE,
    time TIME NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tour_availabilities (
    id SERIAL PRIMARY KEY,
    tour_id INT REFERENCES tours(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time TIME NOT NULL,
    available_tickets INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS transport_availabilities (
    id SERIAL PRIMARY KEY,
    transport_id INT REFERENCES transports(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time TIME NOT NULL,
    available_seats INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INT REFERENCES carts(id) ON DELETE CASCADE,
    tour_id INT REFERENCES tours(id) ON DELETE SET NULL,
    transport_id INT REFERENCES transports(id) ON DELETE SET NULL,
    package_id INT REFERENCES packages(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    quantity INT DEFAULT 1,
    total_price DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    tour_id INT REFERENCES tours(id) ON DELETE SET NULL,
    transport_id INT REFERENCES transports(id) ON DELETE SET NULL,
    package_id INT REFERENCES packages(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status booking_status_enum NOT NULL DEFAULT 'Confirmed'
);
"""


def create_tables():
    """Create tables in the database."""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(CREATE_TABLES_SQL)
                conn.commit()
                logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def fetch_tours(db):
    """Fetch tours from the database."""
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM tours")
        return [
            Tour(
                id=row[0],
                name=row[1],
                description=row[2],
                price_A=row[3],
                price_B=row[4],
                price_C=row[5],
                start_time=row[6],
                end_time=row[7],
                max_tickets=row[8],
                location_url=row[9]
            ) for row in cursor.fetchall()
        ]


def fetch_transports(db):
    """Fetch transports from the database."""
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM transports")
        return [
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
            ) for row in cursor.fetchall()
        ]


@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup."""
    try:
        create_tables()
        # Test database connection
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                logger.info("Database connection successful!")
    except OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise RuntimeError("Database connection failed") from e


# Setup template and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(edit_tours.router)
app.include_router(edit_transports.router)
app.include_router(user_management.router)


@app.get("/")
async def home(
        request: Request,
        db=Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Home page with tours and transports."""
    logger.info("Entered home route")

    try:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "tours": fetch_tours(db),
            "transports": fetch_transports(db),
            "user": current_user
        })
    except Exception as e:
        logger.error(f"Error loading home page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")