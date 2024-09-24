# routers/admin.py
from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from dependencies import admin_required, get_db
from models import Tour, User, UserRoleEnum
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from uuid import uuid4

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user=Depends(admin_required)):
    tours = db.query(Tour).all()
    users = db.query(User).all()
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "tours": tours, "users": users})

@router.post("/admin/create_tour")
async def create_tour(
    name: str = Form(...),
    description: str = Form(...),
    price_A: float = Form(...),
    price_B: float = Form(...),
    price_C: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
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
    return RedirectResponse(url="/admin", status_code=303)

# Add routes for editing and deleting tours, updating user roles, etc.
