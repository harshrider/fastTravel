# routers/edit_tours.py
from datetime import date, datetime, timedelta
from typing import List
from uuid import uuid4
import os
from fastapi import APIRouter, Depends, Request, HTTPException, Form, UploadFile, File,status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from dependencies import get_db, employee_required, logger
from models import Tour, Tag, Image, TourAvailability, User, Transport
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin/tours", tags=["tours"])
templates = Jinja2Templates(directory="templates")


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
        cancellation_policy: str = Form(...),
        refund_policy: str = Form(...),
        rate_a: str = Form(...),
        rate_b: str = Form(...),
        rate_c: str = Form(...),
        location_url: str = Form(None),
        transport_ids: List[int] = Form([]),
        tags: str = Form(''),
        images: List[UploadFile] = File(None),
        start_date: date = Form(...),  # Corrected type
        end_date: date = Form(...),  # Corrected type
        db: Session = Depends(get_db),
        current_user: User = Depends(employee_required)
):
    try:
        # Convert time strings to time objects
        start_time_obj = datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M").time()

        # Create new tour with all fields
        new_tour = Tour(
            name=name,
            description=description,
            price_A=price_A,
            price_B=price_B,
            price_C=price_C,
            start_time=start_time_obj,
            end_time=end_time_obj,
            max_tickets=max_tickets,
            cancellation_policy=cancellation_policy,
            refund_policy=refund_policy,
            rate_a=rate_a,
            rate_b=rate_b,
            rate_c=rate_c,
            location_url=location_url
        )

        # Handle transports
        if transport_ids:
            transports = db.query(Transport).filter(Transport.id.in_(transport_ids)).all()
            new_tour.transports = transports

        # Handle tags
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            for tag_name in tag_list:
                tag = db.query(Tag).filter(func.lower(Tag.name) == func.lower(tag_name)).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()  # Commit to get tag ID
                new_tour.tags.append(tag)

        db.add(new_tour)
        db.commit()
        db.refresh(new_tour)

        # Create availability records
        delta = end_date - start_date
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            db.add(TourAvailability(
                tour_id=new_tour.id,
                date=current_date,
                time=datetime.strptime("00:00", "%H:%M").time(),  # Set actual time
                available_tickets=max_tickets
            ))

        # Handle image uploads
        if images:
            upload_dir = "static/uploads"
            os.makedirs(upload_dir, exist_ok=True)

            for image in images:
                if image.content_type not in ['image/jpeg', 'image/png']:
                    continue

                # Generate unique filename
                file_ext = os.path.splitext(image.filename)[1]
                unique_name = f"{uuid4().hex}{file_ext}"
                file_path = os.path.join(upload_dir, unique_name)

                # Save file
                with open(file_path, "wb") as buffer:
                    buffer.write(await image.read())

                # Create image record
                db.add(Image(
                    url=f"/static/uploads/{unique_name}",
                    tour_id=new_tour.id
                ))

        db.commit()
        logger.info(f"Tour '{name}' created successfully with ID {new_tour.id}")
        return RedirectResponse(url="/admin/tours", status_code=303)

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating tour: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create tour. Please try again."
        )


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
