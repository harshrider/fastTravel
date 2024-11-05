
# routers/admin.py
from fastapi import APIRouter, Depends, Request, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import Tour, User, UserRoleEnum, Transport, Tag, Image
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from uuid import uuid4
from typing import Optional, List
import logging

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
        tags = db.query(Tag).all()  # Fetch all tags for display
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
        images: List[UploadFile] = File(None),
        tags: str = Form(...),  # e.g., "Gold,Adventure"
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    tag_names = [tag.strip() for tag in tags.split(',')]
    tag_objects = [db.query(Tag).filter_by(name=name).first() or Tag(name=name) for name in tag_names]

    # Handle image upload logic
    image_urls = []
    for image in images:
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"
        upload_directory = "static/uploads"
        os.makedirs(upload_directory, exist_ok=True)
        file_path = os.path.join(upload_directory, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
        image_url = f"/static/uploads/{unique_filename}"
        image_urls.append(Image(url=image_url))

    # Save new Tour with tags and images
    new_tour = Tour(name=name, description=description, price_A=price_A, price_B=price_B, price_C=price_C, tags=tag_objects, images=image_urls)
    db.add(new_tour)
    db.commit()
    logger.info(f"Tour '{name}' created successfully with ID {new_tour.id}")
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/delete_tour/{tour_id}")
def delete_tour(tour_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    logger.info(f"Admin '{current_user.username}' is deleting tour with ID {tour_id}")
    try:
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            logger.warning(f"Tour with ID {tour_id} not found.")
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
