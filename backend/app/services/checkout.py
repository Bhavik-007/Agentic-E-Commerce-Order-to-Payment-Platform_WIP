from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import razorpay
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models.cart import Cart, CartItem
from ..models.order import Order, OrderItem
from ..models.payment import Payment
from ..models.catalog import Product
from ..core.config import get_settings

settings = get_settings()


def create_test_checkout(db: Session, user_id: int) -> Payment:
    cart = db.scalar(select(Cart).options(selectinload(Cart.items).selectinload(CartItem.product)).where(Cart.user_id == user_id, Cart.status == "OPEN"))
    if not cart or not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Add an item to your bag before checkout.")
    subtotal = sum((item.unit_price * item.quantity for item in cart.items), Decimal("0"))
    order = Order(user_id=user_id, order_number=f"SP-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}", subtotal=subtotal, total_amount=subtotal)
    db.add(order)
    db.flush()
    for item in cart.items:
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, product_name=item.product.name, quantity=item.quantity, unit_price=item.unit_price, total_price=item.unit_price * item.quantity))
    payment = Payment(order_id=order.id, user_id=user_id, razorpay_order_id=f"order_test_{uuid4().hex[:14]}", amount=subtotal, status="CREATED")
    db.add(payment)
    cart.status = "CHECKED_OUT"
    db.commit()
    db.refresh(payment)
    return payment


def create_razorpay_checkout(db: Session, user_id: int) -> Payment:
    """Create an order in Razorpay Test Mode; the secret stays on this server."""
    cart = db.scalar(select(Cart).options(selectinload(Cart.items).selectinload(CartItem.product)).where(Cart.user_id == user_id, Cart.status == "OPEN"))
    if not cart or not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Add an item to your bag before checkout.")
    subtotal = sum((item.unit_price * item.quantity for item in cart.items), Decimal("0"))
    order = Order(user_id=user_id, order_number=f"SP-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}", subtotal=subtotal, total_amount=subtotal)
    db.add(order)
    db.flush()
    try:
        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        razorpay_order = client.order.create({"amount": int(subtotal * 100), "currency": "INR", "receipt": order.order_number, "notes": {"shoppilot_order": order.order_number}})
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not create Razorpay test order: {error}")
    for item in cart.items:
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, product_name=item.product.name, quantity=item.quantity, unit_price=item.unit_price, total_price=item.unit_price * item.quantity))
    payment = Payment(order_id=order.id, user_id=user_id, razorpay_order_id=razorpay_order["id"], amount=subtotal, status="CREATED")
    db.add(payment)
    cart.status = "CHECKED_OUT"
    db.commit()
    db.refresh(payment)
    return payment


def create_quick_checkout(db: Session, user_id: int, product_id: int, quantity: int) -> Payment:
    """Create a test-mode checkout from an assistant-approved catalog item."""
    product = db.scalar(select(Product).where(Product.id == product_id, Product.is_active == True))  # noqa: E712
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This suggested product is no longer available.")
    total = product.final_price * quantity
    order = Order(user_id=user_id, order_number=f"SP-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}", subtotal=total, total_amount=total)
    db.add(order)
    db.flush()
    db.add(OrderItem(order_id=order.id, product_id=product.id, product_name=product.name, quantity=quantity, unit_price=product.final_price, total_price=total))
    payment = Payment(order_id=order.id, user_id=user_id, razorpay_order_id=f"order_test_{uuid4().hex[:14]}", amount=total, status="CREATED")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def create_razorpay_quick_checkout(db: Session, user_id: int, product_id: int, quantity: int) -> Payment:
    product = db.scalar(select(Product).where(Product.id == product_id, Product.is_active == True))  # noqa: E712
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This suggested product is no longer available.")
    total = product.final_price * quantity
    order = Order(user_id=user_id, order_number=f"SP-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}", subtotal=total, total_amount=total)
    db.add(order)
    db.flush()
    try:
        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        razorpay_order = client.order.create({"amount": int(total * 100), "currency": "INR", "receipt": order.order_number, "notes": {"shoppilot_order": order.order_number, "source": "ai_shortlist"}})
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not create Razorpay test order: {error}")
    db.add(OrderItem(order_id=order.id, product_id=product.id, product_name=product.name, quantity=quantity, unit_price=product.final_price, total_price=total))
    payment = Payment(order_id=order.id, user_id=user_id, razorpay_order_id=razorpay_order["id"], amount=total, status="CREATED")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def verify_test_payment(db: Session, payment: Payment) -> Payment:
    if payment.status != "CREATED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This payment is no longer awaiting completion.")
    payment.status = "CAPTURED"
    payment.payment_method = "TEST_CARD"
    payment.razorpay_payment_id = f"pay_test_{uuid4().hex[:14]}"
    payment.order.status = "PAID"
    db.commit()
    db.refresh(payment)
    return payment


def verify_razorpay_payment(db: Session, payment: Payment, razorpay_payment_id: str, razorpay_signature: str) -> Payment:
    if payment.status != "CREATED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This payment is no longer awaiting completion.")
    try:
        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        client.utility.verify_payment_signature({"razorpay_order_id": payment.razorpay_order_id, "razorpay_payment_id": razorpay_payment_id, "razorpay_signature": razorpay_signature})
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay payment signature verification failed.")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not verify Razorpay payment: {error}")
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.payment_method = "RAZORPAY_TEST"
    payment.status = "CAPTURED"
    payment.order.status = "PAID"
    db.commit()
    db.refresh(payment)
    return payment
