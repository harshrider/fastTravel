# routers/edit_tours.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from dependencies import get_db, employee_required
from models import Tour, Tag, Image, TourAvailability, User
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin/tours", tags=["tours"])
templates = Jinja2Templates(directory="templates")

@router.get("/create", response_class=HTMLResponse)
def create_tour_form(request: Request, current_user: User = Depends(employee_required)):
    return templates.TemplateResponse("edit_tour.html", {"request": request, "user": current_user})

@router.post("/create")
async def create_tour(
    name: str = Form(...),
    description: str = Form(...),
    price_A: float = Form(...),
    price_B: float = Form(...),
    price_C: float = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    max_tickets: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    new_tour = Tour(
        name=name, description=description, price_A=price_A, price_B=price_B, price_C=price_C,
        start_time=start_time, end_time=end_time, max_tickets=max_tickets
    )
    db.add(new_tour)
    db.commit()
    return RedirectResponse(url="/admin/tours", status_code=303)

@router.get("/{tour_id}/edit", response_class=HTMLResponse)
def edit_tour_form(tour_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return templates.TemplateResponse("edit_tour.html", {"request": request, "tour": tour, "user": current_user})

@router.post("/{tour_id}/edit")
async def edit_tour(
    tour_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price_A: float = Form(...),
    price_B: float = Form(...),
    price_C: float = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    max_tickets: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    tour.name = name
    tour.description = description
    tour.price_A = price_A
    tour.price_B = price_B
    tour.price_C = price_C
    tour.start_time = start_time
    tour.end_time = end_time
    tour.max_tickets = max_tickets
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/{tour_id}/delete")
async def delete_tour(tour_id: int, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    db.delete(tour)
    db.commit()
    return RedirectResponse(url="/admin/tours", status_code=303)
