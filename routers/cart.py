# routers/cart.py
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
#from models import Cart, Tour
from database import get_db
from dependencies import get_current_user
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/cart/add")
def add_to_cart(
    tour_id: int = Form(None),
    transport_id: int = Form(None),
    quantity: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Logic to add item to cart
    # ...
    return RedirectResponse(url="/cart", status_code=303)

# @router.get("/cart")
# def view_cart(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     # Logic to display cart items
#     # ...
#     return templates.TemplateResponse("cart.html", {"request": request, "cart_items": cart_items})
