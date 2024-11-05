# routers/transports.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Transport
from fastapi.templating import Jinja2Templates
from dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/transports/{transport_id}")
def transport_detail(transport_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    return templates.TemplateResponse("transport_detail.html", {
        "request": request,
        "transport": transport,
        "tags": transport.tags,     # Pass tags to template
        "images": transport.images, # Pass images to template
        "user": current_user
    })
