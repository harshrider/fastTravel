from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Tour, Transport, TourAvailability, User, Package, Itinerary
from fastapi.templating import Jinja2Templates
from dependencies import get_current_user
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def generate_time_slots(start_time, end_time, interval_minutes=60):
    slots = []
    current_time = datetime.combine(datetime.today(), start_time)
    end_time_dt = datetime.combine(datetime.today(), end_time)
    while current_time <= end_time_dt - timedelta(minutes=interval_minutes):
        slots.append(current_time.time())
        current_time += timedelta(minutes=interval_minutes)
    return slots


# Update your tour detail route
@router.get("/{tour_id}", response_class=HTMLResponse)
async def tour_detail(
        tour_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # Get related data
    transports = db.query(Transport).all()
    packages = db.query(Package).filter(Package.tours.any(id=tour_id)).all()

    return templates.TemplateResponse("tour_detail.html", {
        "request": request,
        "tour": tour,
        "transports": transports,
        "packages": packages,
        "user": current_user,
        "time_slots": generate_time_slots(tour.start_time, tour.end_time)
    })

@router.get("/tours/{tour_id}/available-dates")
def get_available_dates(tour_id: int, db: Session = Depends(get_db)):
    # Fetch availability for the tour
    availabilities = db.query(TourAvailability).filter(
        TourAvailability.tour_id == tour_id,
        TourAvailability.is_available == True,
        TourAvailability.available_tickets > 0
    ).all()

    # Get dates where the tour is unavailable
    unavailable_dates = [
        str(availability.date) for availability in availabilities if availability.available_tickets <= 0
    ]

    return {"unavailable_dates": unavailable_dates}


@router.get("/tours/{tour_id}/package-itinerary/{package_id}")
def get_package_itinerary(tour_id: int, package_id: int, db: Session = Depends(get_db)):
    # Fetch the package by ID and ensure it's associated with the tour
    package = db.query(Package).filter(Package.id == package_id, Package.tours.any(id=tour_id)).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found for this tour")

    # Get itinerary items associated with the package
    itinerary_items = db.query(Itinerary).filter(Itinerary.package_id == package_id).order_by(Itinerary.time).all()

    # Format the itinerary data as a list of dictionaries for JSON response
    itinerary = [{"time": item.time.strftime('%H:%M'), "activity": item.description} for item in itinerary_items]

    return {"itinerary": itinerary}
