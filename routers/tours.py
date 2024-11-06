# routers/tours.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Tour, User
from fastapi.templating import Jinja2Templates
from dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
    return templates.TemplateResponse("tour_detail.html", {
        "request": request,
        "tour": tour,
        "tags": tour.tags,
        "images": tour.images,
        "user": current_user
    })
