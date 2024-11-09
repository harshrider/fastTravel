# routers/admin.py
from fastapi import APIRouter, Depends, Request, HTTPException, status, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import *
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
    location_url: str = Form(None),
    start_date: date = Form(...),
    end_date: date = Form(...),
    images: List[UploadFile] = File(None),
    tags: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M").time()

    # Handle tags
    tag_names = {tag.strip().upper() for tag in tags.split(',') if tag.strip()}
    tag_objects = []
    for tag_name in tag_names:
        existing_tag = db.query(Tag).filter_by(name=tag_name).first()
        if not existing_tag:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)
            tag_objects.append(new_tag)
        else:
            tag_objects.append(existing_tag)

    # Handle images
    image_objects = []
    if images:
        for image in images:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid4()}{file_extension}"
            upload_directory = "static/uploads"
            os.makedirs(upload_directory, exist_ok=True)
            file_path = os.path.join(upload_directory, unique_filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_objects.append(Image(url=f"/static/uploads/{unique_filename}"))

    new_tour = Tour(
        name=name,
        description=description,
        price_A=price_A,
        price_B=price_B,
        price_C=price_C,
        start_time=start_time_obj,
        end_time=end_time_obj,
        max_tickets=max_tickets,
        location_url=location_url,
        tags=tag_objects,
        images=image_objects
    )
    db.add(new_tour)
    db.commit()
    db.refresh(new_tour)

    create_tour_availability(new_tour, start_date, end_date, db)
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
    location_url: str = Form(None),
    start_date: date = Form(...),
    end_date: date = Form(...),
    images: List[UploadFile] = File(None),
    tags: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M").time()

    tag_names = {tag.strip().upper() for tag in tags.split(',') if tag.strip()}
    tag_objects = []
    for tag_name in tag_names:
        existing_tag = db.query(Tag).filter_by(name=tag_name).first()
        if not existing_tag:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)
            tag_objects.append(new_tag)
        else:
            tag_objects.append(existing_tag)

    image_objects = []
    if images:
        for image in images:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid4()}{file_extension}"
            upload_directory = "static/uploads"
            os.makedirs(upload_directory, exist_ok=True)
            file_path = os.path.join(upload_directory, unique_filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_objects.append(Image(url=f"/static/uploads/{unique_filename}"))

    new_transport = Transport(
        name=name,
        description=description,
        price_A=price_A,
        price_B=price_B,
        price_C=price_C,
        start_time=start_time_obj,
        end_time=end_time_obj,
        max_seats=max_seats,
        location_url=location_url,
        tags=tag_objects,
        images=image_objects
    )
    db.add(new_transport)
    db.commit()
    db.refresh(new_transport)

    create_transport_availability(new_transport, start_date, end_date, db)
    logger.info(f"Transport '{name}' created successfully with ID {new_transport.id}")
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/delete_tour/{tour_id}")
def delete_tour(tour_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    if tour.images:
        for image in tour.images:
            image_path = os.path.join("static", image.url.lstrip("/"))
            if os.path.exists(image_path):
                os.remove(image_path)
    db.delete(tour)
    db.commit()
    logger.info(f"Tour with ID {tour_id} deleted successfully.")
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/delete_transport/{transport_id}")
def delete_transport(transport_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    if transport.images:
        for image in transport.images:
            image_path = os.path.join("static", image.url.lstrip("/"))
            if os.path.exists(image_path):
                os.remove(image_path)
    db.delete(transport)
    db.commit()
    logger.info(f"Transport with ID {transport_id} deleted successfully.")
    return RedirectResponse(url="/admin", status_code=303)

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
    location_url: str = Form(None),
    images: List[UploadFile] = File(None),
    tags: str = Form(""),
    start_date: date = Form(None),
    end_date: date = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    tour.name = name
    tour.description = description
    tour.price_A = price_A
    tour.price_B = price_B
    tour.price_C = price_C
    tour.start_time = datetime.strptime(start_time, "%H:%M").time()
    tour.end_time = datetime.strptime(end_time, "%H:%M").time()
    tour.max_tickets = max_tickets
    tour.location_url = location_url

    tag_names = {tag.strip().upper() for tag in tags.split(',') if tag.strip()}
    tag_objects = []
    for tag_name in tag_names:
        existing_tag = db.query(Tag).filter_by(name=tag_name).first()
        if not existing_tag:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)
            tag_objects.append(new_tag)
        else:
            tag_objects.append(existing_tag)
    tour.tags = tag_objects

    if images:
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

    if start_date and end_date:
        db.query(TourAvailability).filter(
            TourAvailability.tour_id == tour_id,
            TourAvailability.date >= start_date,
            TourAvailability.date <= end_date
        ).delete()
        db.commit()
        create_tour_availability(tour, start_date, end_date, db)

    logger.info(f"Tour '{name}' updated successfully with ID {tour.id}")
    return RedirectResponse(url="/admin", status_code=303)

# Similar routes for editing transports, managing tour and transport availability...
# Include transport edit routes and availability management functions as seen for tours above.

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
    location_url: str = Form(None),
    images: List[UploadFile] = File(None),
    tags: str = Form(""),
    start_date: date = Form(None),
    end_date: date = Form(None),
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
    transport.location_url = location_url

    # Process tags from the input, ensuring they are unique and uppercase
    tag_names = {tag.strip().upper() for tag in tags.split(',') if tag.strip()}
    tag_objects = []
    for tag_name in tag_names:  # 'tag_name' now used consistently in the loop
        # Query for existing tags by the tag_name
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            # Create a new Tag object if it doesn't already exist
            tag = Tag(name=tag_name)
        tag_objects.append(tag)  # Add the tag object to the list

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

    # Update availability if dates are provided
    if start_date and end_date:
        # Delete existing availabilities in the date range
        db.query(TransportAvailability).filter(
            TransportAvailability.transport_id == transport_id,
            TransportAvailability.date >= start_date,
            TransportAvailability.date <= end_date
        ).delete()
        db.commit()
        # Generate new availability
        create_transport_availability(transport, start_date, end_date, db)

    logger.info(f"Transport '{name}' updated successfully with ID {transport.id}")
    return RedirectResponse(url="/admin", status_code=303)

# Routes to manage tour availability
@router.get("/admin/manage_tour_availability/{tour_id}", response_class=HTMLResponse)
def manage_tour_availability(tour_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    availabilities = db.query(TourAvailability).filter(TourAvailability.tour_id == tour_id).all()
    return templates.TemplateResponse("manage_tour_availability.html", {"request": request, "tour": tour, "availabilities": availabilities})

@router.post("/admin/manage_tour_availability/{tour_id}")
def update_tour_availability(
    tour_id: int,
    date: str = Form(...),
    time: str = Form(...),
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
        availability_time = datetime.strptime(time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")

    is_available_bool = is_available.lower() == 'true'

    # Check if availability already exists
    availability = db.query(TourAvailability).filter_by(
        tour_id=tour_id,
        date=availability_date,
        time=availability_time
    ).first()
    if availability:
        # Update existing availability
        availability.available_tickets = available_tickets
        availability.is_available = is_available_bool
    else:
        # Create new availability
        availability = TourAvailability(
            tour_id=tour_id,
            date=availability_date,
            time=availability_time,
            available_tickets=available_tickets,
            is_available=is_available_bool
        )
        db.add(availability)
    db.commit()
    logger.info(f"Updated availability for tour ID {tour_id} on {availability_date} at {availability_time}")
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
    availabilities = db.query(TransportAvailability).filter(TransportAvailability.transport_id == transport_id).all()
    return templates.TemplateResponse("manage_transport_availability.html",
                                      {"request": request, "transport": transport, "availabilities": availabilities})

@router.post("/admin/manage_transport_availability/{transport_id}")
def update_transport_availability(
    transport_id: int,
    date: str = Form(...),
    time: str = Form(...),
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
        availability_time = datetime.strptime(time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")

    is_available_bool = is_available.lower() == 'true'

    # Check if availability already exists
    availability = db.query(TransportAvailability).filter_by(
        transport_id=transport_id,
        date=availability_date,
        time=availability_time
    ).first()
    if availability:
        # Update existing availability
        availability.available_seats = available_seats
        availability.is_available = is_available_bool
    else:
        # Create new availability
        availability = TransportAvailability(
            transport_id=transport_id,
            date=availability_date,
            time=availability_time,
            available_seats=available_seats,
            is_available=is_available_bool
        )
        db.add(availability)
    db.commit()
    logger.info(f"Updated availability for transport ID {transport_id} on {availability_date} at {availability_time}")
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


# routers/admin.py
from fastapi import APIRouter, Depends, Request, HTTPException, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import User, UserRoleEnum
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/admin/update_user_role")
def update_user_role(
        user_id: int = Form(...),
        new_role: str = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        # Update the user's role
        user.role = UserRoleEnum(new_role)
        db.commit()
        db.refresh(user)
        logger.info(f"Updated role for user {user.username} to {new_role}")
    except ValueError:
        logger.error(f"Invalid role value: {new_role}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role value")

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/admin/create_package")
async def create_package(
    name: str = Form(...),
    description: str = Form(...),
    price_A: float = Form(...),
    price_B: float = Form(...),
    price_C: float = Form(...),
    itinerary_times: List[str] = Form(...),  # List of itinerary times
    itinerary_descriptions: List[str] = Form(...),  # List of itinerary descriptions
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    # Create package
    new_package = Package(
        name=name,
        description=description,
        price_A=price_A,
        price_B=price_B,
        price_C=price_C,
    )
    db.add(new_package)
    db.commit()
    db.refresh(new_package)

    # Add itinerary entries
    itinerary_entries = [
        Itinerary(package_id=new_package.id, time=datetime.strptime(itime, "%H:%M").time(), description=idesc)
        for itime, idesc in zip(itinerary_times, itinerary_descriptions)
    ]
    db.bulk_save_objects(itinerary_entries)
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)
