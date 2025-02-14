# routers/edit_tours.py
from datetime import timedelta
from msilib.schema import File

from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from dependencies import get_db, employee_required
from models import Tour, Tag, Image, TourAvailability, User, Transport
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin/tours", tags=["tours"])
templates = Jinja2Templates(directory="templates")

@router.get("/create", response_class=HTMLResponse)
def create_tour_form(request: Request, current_user: User = Depends(employee_required)):
    return templates.TemplateResponse("edit_tour.html", {"request": request, "user": current_user})

@router.post("/create")
async def create_tour(
    # Existing parameters
    name: str = Form(...),
    description: str = Form(...),
    price_A: float = Form(...),
    price_B: float = Form(...),
    price_C: float = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    max_tickets: int = Form(...),
    cancellation_policy: str = Form(...),
    refund_policy: str = Form(...),
    rate_A: str = Form(...),
    rate_B: str = Form(...),
    rate_C: str = Form(...),
    location_url: str = Form(None),
    transport_ids: list[int] = Form([]),
    tags: str = Form(''),
    images: list[UploadFile] = File([]),
    start_date: 2/14/2025 = Form(...),  # Add these
    end_date: 2/14/2030 = Form(...),    # Add these
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    try:
        # Create new tour with all fields
        new_tour = Tour(
            name=name,
            description=description,
            price_A=price_A,
            price_B=price_B,
            price_C=price_C,
            start_time=start_time,
            end_time=end_time,
            max_tickets=max_tickets,
            cancellation_policy=cancellation_policy,
            refund_policy=refund_policy,
            rate_A=rate_A,
            rate_B=rate_B,
            rate_C=rate_C,
            location_url=location_url
        )

        # Handle transports
        transports = db.query(Transport).filter(Transport.id.in_(transport_ids)).all()
        new_tour.transports = transports

        # Handle tags
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            for tag_name in tag_list:
                tag = db.query(Tag).filter(func.lower(Tag.name) == func.lower(tag_name)).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                new_tour.tags.append(tag)

        db.add(new_tour)
        db.commit()

        # Create availability records
        delta = end_date - start_date
        for i in range(delta.days + 1):
            date = start_date + timedelta(days=i)
            db.add(TourAvailability(
                tour_id=new_tour.id,
                date=date,
                available_tickets=max_tickets,
                price_modifier=0.0
            ))

        # Handle image uploads
        for image in images:
            if image.content_type not in ['image/jpeg', 'image/png']:
                continue
            # Implement your actual image storage logic here
            image_url = f"/static/uploads/{image.filename}"
            db.add(Image(url=image_url, tour_id=new_tour.id))

        db.commit()
        return RedirectResponse(url="/admin/tours", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



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
