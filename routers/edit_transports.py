# routers/edit_transports.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from dependencies import get_db, employee_required
from models import Transport, User
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin/transports", tags=["transports"])
templates = Jinja2Templates(directory="templates")

@router.get("/create", response_class=HTMLResponse)
def create_transport_form(request: Request, current_user: User = Depends(employee_required)):
    return templates.TemplateResponse("edit_transport.html", {"request": request, "user": current_user})

@router.post("/create")
async def create_transport(
    name: str = Form(...),
    description: str = Form(...),
    price_A: float = Form(...),
    price_B: float = Form(...),
    price_C: float = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    max_seats: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    new_transport = Transport(
        name=name, description=description, price_A=price_A, price_B=price_B, price_C=price_C,
        start_time=start_time, end_time=end_time, max_seats=max_seats
    )
    db.add(new_transport)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/{transport_id}/edit", response_class=HTMLResponse)
def edit_transport_form(transport_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    return templates.TemplateResponse("edit_transport.html", {"request": request, "transport": transport, "user": current_user})

@router.post("/{transport_id}/edit")
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
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    transport.name = name
    transport.description = description
    transport.price_A = price_A
    transport.price_B = price_B
    transport.price_C = price_C
    transport.start_time = start_time
    transport.end_time = end_time
    transport.max_seats = max_seats
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/{transport_id}/delete")
async def delete_transport(transport_id: int, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    db.delete(transport)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)
