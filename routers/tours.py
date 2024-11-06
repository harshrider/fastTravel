from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Tour, User
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

@router.get("/tours/{tour_id}")
def tour_detail(
    tour_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # Generate time slots for the tour
    time_slots = generate_time_slots(tour.start_time, tour.end_time)

    return templates.TemplateResponse("tour_detail.html", {
        "request": request,
        "tour": tour,
        "tags": tour.tags,
        "images": tour.images,
        "user": current_user,
        "time_slots": time_slots
    })
