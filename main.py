import logging
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# Local imports
from database import get_db
from models import User, Tour, Transport
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

# Template and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Test database connection
try:
    with get_db() as conn:  # Directly use your existing context manager
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info("Database connection successful!")
except OperationalError as e:
    logger.error(f"Database connection failed: {str(e)}")
    raise RuntimeError("Database connection failed") from e

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
        db=Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    logger.info("Entered home route")

    if current_user:
        logger.info(f"User '{current_user.username}' is accessing the home page.")
    else:
        logger.info("Unauthenticated user is accessing the home page.")

    try:
        # Get tours
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM tours")
            tours_data = cursor.fetchall()
            tours = [
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
                ) for row in tours_data
            ]

        # Get transports
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM transports")
            transports_data = cursor.fetchall()
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
        logger.error(f"Error querying database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tours": tours,
        "transports": transports,
        "user": current_user
    })