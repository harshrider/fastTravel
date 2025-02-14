# routers/admin.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from dependencies import get_db, employee_required
from models import User, Tour, Transport
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "user": current_user}
    )
@router.get("/admin/tours", response_class=HTMLResponse)
async def manage_tours(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    tours = db.query(Tour).all()
    return templates.TemplateResponse("edit_tour.html", {
        "request": request,
        "user": current_user,
        "tours": tours
    })

@router.get("/admin/transports", response_class=HTMLResponse)
async def manage_transports(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    transports = db.query(Transport).all()
    return templates.TemplateResponse("edit_transport.html", {
        "request": request,
        "user": current_user,
        "transports": transports
    })

@router.get("/admin/users", response_class=HTMLResponse)
async def manage_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    users = db.query(User).all()
    return templates.TemplateResponse("edit_user.html", {
        "request": request,
        "user": current_user,
        "users": users
    })