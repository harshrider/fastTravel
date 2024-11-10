# routers/user_management.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from dependencies import get_db, superuser_required
from models import User, UserRoleEnum
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin/users", tags=["users"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def manage_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(superuser_required)
):
    users = db.query(User).all()
    return templates.TemplateResponse(
        "manage_users.html",
        {"request": request, "users": users, "user": current_user}
    )

@router.post("/update_role")
def update_user_role(
    user_id: int = Form(...),
    new_role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(superuser_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = UserRoleEnum(new_role)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/delete")
def delete_user(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(superuser_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)
