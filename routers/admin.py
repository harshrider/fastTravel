# routers/admin.py
from fastapi import APIRouter, Depends, Request, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import Tour, User, UserRoleEnum, Transport
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from uuid import uuid4
from typing import Optional
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
    except Exception as e:
        logger.error(f"Error retrieving admin dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "tours": tours, "users": users, "transports": transports})

@router.post("/admin/create_tour")
async def create_tour(
        name: str = Form(...),
        description: str = Form(...),
        price_A: float = Form(...),
        price_B: float = Form(...),
        price_C: float = Form(...),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    logger.info(f"Admin '{current_user.username}' is creating a new tour: {name}")
    try:
        # Handle image upload
        image_url = None
        if image:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid4()}{file_extension}"
            upload_directory = "static/uploads"
            os.makedirs(upload_directory, exist_ok=True)
            file_path = os.path.join(upload_directory, unique_filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_url = f"/static/uploads/{unique_filename}"
            logger.info(f"Image uploaded for tour '{name}' at {image_url}")

        new_tour = Tour(
            name=name,
            description=description,
            price_A=price_A,
            price_B=price_B,
            price_C=price_C,
            image_url=image_url
        )
        db.add(new_tour)
        db.commit()
        logger.info(f"Tour '{name}' created successfully with ID {new_tour.id}")
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        logger.error(f"Error creating tour '{name}': {e}")
        raise HTTPException(status_code=500, detail="Failed to create tour")

@router.post("/admin/delete_tour/{tour_id}")
def delete_tour(tour_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    logger.info(f"Admin '{current_user.username}' is deleting tour with ID {tour_id}")
    try:
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            logger.warning(f"Tour with ID {tour_id} not found.")
            raise HTTPException(status_code=404, detail="Tour not found")
        # Optionally, delete the associated image file
        if tour.image_url:
            image_path = os.path.join("static", tour.image_url.lstrip("/"))
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

@router.post("/admin/update_user_role")
def update_user_role(
        user_id: int = Form(...),
        new_role: UserRoleEnum = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    logger.info(f"Admin '{current_user.username}' is updating role for user ID {user_id} to '{new_role}'")
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            raise HTTPException(status_code=404, detail="User not found")
        old_role = user.role
        user.role = new_role
        db.commit()
        logger.info(f"User ID {user_id} role updated from '{old_role}' to '{new_role}'")
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        logger.error(f"Error updating user role for ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user role")
