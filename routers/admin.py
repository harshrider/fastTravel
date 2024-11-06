from fastapi import APIRouter, Depends, Request, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import Tour, Transport, User, UserRoleEnum, Tag, Image
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from uuid import uuid4
from typing import List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import Tour, Transport, User, UserRoleEnum, Tag, Image, TourAvailability, TransportAvailability
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from uuid import uuid4
from typing import List
import logging
from datetime import datetime, date

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    logger.info(f"Admin '{current_user.username}' is accessing the dashboard.")
    try:
        tours = db.query(Tour).all()
        transports = db.query(Transport).all()
        users = db.query(User).all()
        tags = db.query(Tag).all()
    except Exception as e:
        logger.error(f"Error retrieving admin dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "tours": tours, "users": users, "transports": transports, "tags": tags})

@router.post("/admin/create_tour")
async def create_tour(
        name: str = Form(...),
        description: str = Form(...),
        price_A: float = Form(...),
        price_B: float = Form(...),
        price_C: float = Form(...),
        start_time: str = Form(...),
        end_time: str = Form(...),
        max_tickets: int = Form(...),
        images: List[UploadFile] = File(None),
        tags: str = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M").time()

    tag_names = {tag.strip().upper() for tag in tags.split(',')}
    tag_objects = [db.query(Tag).filter_by(name=name).first() or Tag(name=name) for name in tag_names]

    image_urls = []
    for image in images:
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"
        upload_directory = "static/uploads"
        os.makedirs(upload_directory, exist_ok=True)
        file_path = os.path.join(upload_directory, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
        image_urls.append(Image(url=f"/static/uploads/{unique_filename}"))

    new_tour = Tour(
        name=name,
        description=description,
        price_A=price_A,
        price_B=price_B,
        price_C=price_C,
        start_time=start_time_obj,
        end_time=end_time_obj,
        max_tickets=max_tickets,
        tags=tag_objects,
        images=image_urls
    )
    db.add(new_tour)
    db.commit()
    logger.info(f"Tour '{name}' created successfully with ID {new_tour.id}")
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/create_transport")
async def create_transport(
        name: str = Form(...),
        description: str = Form(...),
        price_A: float = Form(...),
        price_B: float = Form(...),
        price_C: float = Form(...),
        start_time: str = Form(...),
        end_time: str = Form(...),
        max_seats: int = Form(...),
        images: List[UploadFile] = File(None),
        tags: str = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M").time()

    tag_names = {tag.strip().upper() for tag in tags.split(',')}
    tag_objects = [db.query(Tag).filter_by(name=name).first() or Tag(name=name) for name in tag_names]

    image_urls = []
    for image in images:
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"
        upload_directory = "static/uploads"
        os.makedirs(upload_directory, exist_ok=True)
        file_path = os.path.join(upload_directory, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
        image_urls.append(Image(url=f"/static/uploads/{unique_filename}"))

    new_transport = Transport(
        name=name,
        description=description,
        price_A=price_A,
        price_B=price_B,
        price_C=price_C,
        start_time=start_time_obj,
        end_time=end_time_obj,
        max_seats=max_seats,
        tags=tag_objects,
        images=image_urls
    )
    db.add(new_transport)
    db.commit()
    logger.info(f"Transport '{name}' created successfully with ID {new_transport.id}")
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/delete_tour/{tour_id}")
def delete_tour(tour_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    logger.info(f"Admin '{current_user.username}' is deleting tour with ID {tour_id}")
    try:
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            logger.warning(f"Tour with ID {tour_id} not foundd.")
            raise HTTPException(status_code=404, detail="Tour not found")
        if tour.images:
            for image in tour.images:
                image_path = os.path.join("static", image.url.lstrip("/"))
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.info(f"Deleted image file for tour ID {tour_id}: {image_path}")
        db.delete(tour)
        db.commit()
        logger.info(f"Tour with ID {tour_id} deleted successfully.")
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        logger.error(f"Error deleting tour ID {tour_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete tour")

@router.get("/admin/edit_tour/{tour_id}", response_class=HTMLResponse)
def edit_tour_form(tour_id: int, request: Request, db: Session = Depends(get_db),
                       current_user: User = Depends(admin_required)):
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        return templates.TemplateResponse("edit_tour.html", {"request": request, "tour": tour})

@router.post("/admin/edit_tour/{tour_id}")
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
            images: List[UploadFile] = File(None),
            tags: str = Form(""),
            db: Session = Depends(get_db),
            current_user: User = Depends(admin_required)
    ):
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")

        # Update tour fields
        tour.name = name
        tour.description = description
        tour.price_A = price_A
        tour.price_B = price_B
        tour.price_C = price_C
        tour.start_time = datetime.strptime(start_time, "%H:%M").time()
        tour.end_time = datetime.strptime(end_time, "%H:%M").time()
        tour.max_tickets = max_tickets

        # Update tags
        tag_names = {tag.strip().upper() for tag in tags.split(',') if tag.strip()}
        tag_objects = []
        for name in tag_names:
            tag = db.query(Tag).filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
            tag_objects.append(tag)
        tour.tags = tag_objects

        # Update images if new images are uploaded
        if images:
            # Delete old images
            if tour.images:
                for image in tour.images:
                    image_path = os.path.join("static", image.url.lstrip("/"))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    db.delete(image)
            image_urls = []
            for image in images:
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"{uuid4()}{file_extension}"
                upload_directory = "static/uploads"
                os.makedirs(upload_directory, exist_ok=True)
                file_path = os.path.join(upload_directory, unique_filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await image.read())
                image_urls.append(Image(url=f"/static/uploads/{unique_filename}"))
            tour.images = image_urls

        db.commit()
        logger.info(f"Tour '{name}' updated successfully with ID {tour.id}")
        return RedirectResponse(url="/admin", status_code=303)

# Similar routes for editing transports
@router.get("/admin/edit_transport/{transport_id}", response_class=HTMLResponse)
def edit_transport_form(transport_id: int, request: Request, db: Session = Depends(get_db),
                            current_user: User = Depends(admin_required)):
        transport = db.query(Transport).filter(Transport.id == transport_id).first()
        if not transport:
            raise HTTPException(status_code=404, detail="Transport not found")
        return templates.TemplateResponse("edit_transport.html", {"request": request, "transport": transport})

@router.post("/admin/edit_transport/{transport_id}")
async def edit_transport(
            transport_id: int,
            name: str = Form(...),
            description: str = Form(...),
            price_A: float = Form(...),
            price_B: float = Form(...),
            price_C: float = Form(...),
            start_time: str = Form(...),
            end_time: str = Form(...),
            max_seats: int = Form(...),
            images: List[UploadFile] = File(None),
            tags: str = Form(""),
            db: Session = Depends(get_db),
            current_user: User = Depends(admin_required)
    ):
        transport = db.query(Transport).filter(Transport.id == transport_id).first()
        if not transport:
            raise HTTPException(status_code=404, detail="Transport not found")

        # Update transport fields
        transport.name = name
        transport.description = description
        transport.price_A = price_A
        transport.price_B = price_B
        transport.price_C = price_C
        transport.start_time = datetime.strptime(start_time, "%H:%M").time()
        transport.end_time = datetime.strptime(end_time, "%H:%M").time()
        transport.max_seats = max_seats

        # Update tags
        tag_names = {tag.strip().upper() for tag in tags.split(',') if tag.strip()}
        tag_objects = []
        for name in tag_names:
            tag = db.query(Tag).filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
            tag_objects.append(tag)
        transport.tags = tag_objects

        # Update images if new images are uploaded
        if images:
            # Delete old images
            if transport.images:
                for image in transport.images:
                    image_path = os.path.join("static", image.url.lstrip("/"))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    db.delete(image)
            image_urls = []
            for image in images:
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"{uuid4()}{file_extension}"
                upload_directory = "static/uploads"
                os.makedirs(upload_directory, exist_ok=True)
                file_path = os.path.join(upload_directory, unique_filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await image.read())
                image_urls.append(Image(url=f"/static/uploads/{unique_filename}"))
            transport.images = image_urls

        db.commit()
        logger.info(f"Transport '{name}' updated successfully with ID {transport.id}")
        return RedirectResponse(url="/admin", status_code=303)

    # Routes to manage tour availability

@router.get("/admin/manage_tour_availability/{tour_id}", response_class=HTMLResponse)
def manage_tour_availability(tour_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        return templates.TemplateResponse("manage_tour_availability.html", {"request": request, "tour": tour})

@router.post("/admin/manage_tour_availability/{tour_id}")
def update_tour_availability(
            tour_id: int,
            date: str = Form(...),
            available_tickets: int = Form(...),
            is_available: str = Form(...),
            db: Session = Depends(get_db),
            current_user: User = Depends(admin_required)
    ):
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")

        try:
            availability_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        is_available_bool = is_available.lower() == 'true'

        # Check if availability already exists
        availability = db.query(TourAvailability).filter_by(tour_id=tour_id, date=availability_date).first()
        if availability:
            # Update existing availability
            availability.available_tickets = available_tickets
            availability.is_available = is_available_bool
        else:
            # Create new availability
            availability = TourAvailability(
                tour_id=tour_id,
                date=availability_date,
                available_tickets=available_tickets,
                is_available=is_available_bool
            )
            db.add(availability)
        db.commit()
        logger.info(f"Updated availability for tour ID {tour_id} on {availability_date}")
        return RedirectResponse(url=f"/admin/manage_tour_availability/{tour_id}", status_code=303)

@router.post("/admin/delete_tour_availability/{availability_id}")
def delete_tour_availability(availability_id: int, db: Session = Depends(get_db),
                                 current_user: User = Depends(admin_required)):
        availability = db.query(TourAvailability).filter(TourAvailability.id == availability_id).first()
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        tour_id = availability.tour_id
        db.delete(availability)
        db.commit()
        logger.info(f"Deleted availability ID {availability_id} for tour ID {tour_id}")
        return RedirectResponse(url=f"/admin/manage_tour_availability/{tour_id}", status_code=303)

    # Similar routes for managing transport availability

@router.get("/admin/manage_transport_availability/{transport_id}", response_class=HTMLResponse)
def manage_transport_availability(transport_id: int, request: Request, db: Session = Depends(get_db),
                                      current_user: User = Depends(admin_required)):
        transport = db.query(Transport).filter(Transport.id == transport_id).first()
        if not transport:
            raise HTTPException(status_code=404, detail="Transport not found")
        return templates.TemplateResponse("manage_transport_availability.html",
                                          {"request": request, "transport": transport})

@router.post("/admin/manage_transport_availability/{transport_id}")
def update_transport_availability(
            transport_id: int,
            date: str = Form(...),
            available_seats: int = Form(...),
            is_available: str = Form(...),
            db: Session = Depends(get_db),
            current_user: User = Depends(admin_required)
    ):
        transport = db.query(Transport).filter(Transport.id == transport_id).first()
        if not transport:
            raise HTTPException(status_code=404, detail="Transport not found")

        try:
            availability_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        is_available_bool = is_available.lower() == 'true'

        # Check if availability already exists
        availability = db.query(TransportAvailability).filter_by(transport_id=transport_id,
                                                                 date=availability_date).first()
        if availability:
            # Update existing availability
            availability.available_seats = available_seats
            availability.is_available = is_available_bool
        else:
            # Create new availability
            availability = TransportAvailability(
                transport_id=transport_id,
                date=availability_date,
                available_seats=available_seats,
                is_available=is_available_bool
            )
            db.add(availability)
        db.commit()
        logger.info(f"Updated availability for transport ID {transport_id} on {availability_date}")
        return RedirectResponse(url=f"/admin/manage_transport_availability/{transport_id}", status_code=303)

@router.post("/admin/delete_transport_availability/{availability_id}")
def delete_transport_availability(availability_id: int, db: Session = Depends(get_db),
                                      current_user: User = Depends(admin_required)):
        availability = db.query(TransportAvailability).filter(TransportAvailability.id == availability_id).first()
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        transport_id = availability.transport_id
        db.delete(availability)
        db.commit()
        logger.info(f"Deleted availability ID {availability_id} for transport ID {transport_id}")
        return RedirectResponse(url=f"/admin/manage_transport_availability/{transport_id}", status_code=303)

