# routers/cart.py
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import Cart, CartItem, Tour, Transport, User
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from fpdf import FPDF
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/cart/add")
def add_to_cart(
    tour_id: Optional[int] = Form(None),
    transport_id: Optional[int] = Form(None),
    quantity: int = Form(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Fetch or create cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Add item to cart
    if tour_id:
        tour = db.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.tour_id == tour_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, tour_id=tour_id, quantity=quantity)
            db.add(cart_item)
    elif transport_id:
        transport = db.query(Transport).filter(Transport.id == transport_id).first()
        if not transport:
            raise HTTPException(status_code=404, detail="Transport not found")
        cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.transport_id == transport_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, transport_id=transport_id, quantity=quantity)
            db.add(cart_item)
    else:
        raise HTTPException(status_code=400, detail="No tour or transport specified")

    db.commit()
    return RedirectResponse(url="/cart", status_code=303)

@router.get("/cart")
def view_cart(request: Request, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    cart_items = []
    if cart:
        for item in cart.items:
            if item.tour:
                price = item.tour.price_A if current_user.role == "A" else \
                        item.tour.price_B if current_user.role == "B" else \
                        item.tour.price_C
                cart_items.append({
                    "id": item.id,
                    "type": "Tour",
                    "name": item.tour.name,
                    "description": item.tour.description,
                    "price": price,
                    "quantity": item.quantity,
                    "total": price * item.quantity
                })
            elif item.transport:
                price = item.transport.price_A if current_user.role == "A" else \
                        item.transport.price_B if current_user.role == "B" else \
                        item.transport.price_C
                cart_items.append({
                    "id": item.id,
                    "type": "Transport",
                    "name": item.transport.name,
                    "price": price,
                    "quantity": item.quantity,
                    "total": price * item.quantity
                })

    return templates.TemplateResponse("cart.html", {"request": request, "cart_items": cart_items, "user": current_user})

@router.post("/cart/remove")
def remove_from_cart(
    item_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return RedirectResponse(url="/cart", status_code=303)

@router.get("/cart/download_itinerary")
def download_itinerary(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=404, detail="Cart is empty")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Tour Itinerary", ln=True, align='C')
    pdf.ln(10)

    # Tours Section
    pdf.cell(200, 10, txt="Tours", ln=True, align='L')
    pdf.cell(80, 10, txt="Tour", border=1)
    pdf.cell(60, 10, txt="No. Of People", border=1)
    pdf.cell(40, 10, txt="Price", border=1)
    pdf.ln(10)

    for item in cart.items:
        if item.tour:
            pdf.cell(80, 10, txt=item.tour.name, border=1)
            pdf.cell(60, 10, txt=str(item.quantity), border=1)
            pdf.cell(40, 10, txt="", border=1)
            pdf.ln(10)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(180, 10, txt=f"Description: {item.tour.description}")
            pdf.set_font("Arial", size=12)
            pdf.ln(5)

    pdf.ln(10)

    # Transports Section
    pdf.cell(200, 10, txt="Transports", ln=True, align='L')
    pdf.cell(80, 10, txt="Transport", border=1)
    pdf.cell(60, 10, txt="No. Of People", border=1)
    pdf.cell(40, 10, txt="Price", border=1)
    pdf.ln(10)

    for item in cart.items:
        if item.transport:
            pdf.cell(80, 10, txt=item.transport.name, border=1)
            pdf.cell(60, 10, txt=str(item.quantity), border=1)
            pdf.cell(40, 10, txt="", border=1)
            pdf.ln(10)

    pdf_output_path = f"static/itinerary_{current_user.id}.pdf"
    pdf.output(pdf_output_path)

    return FileResponse(pdf_output_path, media_type='application/pdf', filename="itinerary.pdf")
