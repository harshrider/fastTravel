# # routers/admin.py
# from fastapi import APIRouter, Depends, Request
# from fastapi.responses import HTMLResponse
# from sqlalchemy.orm import Session
# from dependencies import get_db, employee_required
# from models import User
# from fastapi.templating import Jinja2Templates
#
# router = APIRouter()
# templates = Jinja2Templates(directory="templates")
#
# @router.get("/admin", response_class=HTMLResponse)
# def admin_dashboard(
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(employee_required)
# ):
#     return templates.TemplateResponse(
#         "admin_dashboard.html",
#         {"request": request, "user": current_user}
#     )
