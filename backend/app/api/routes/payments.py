from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...api.deps import get_current_user
from ...core.config import get_settings
from ...core.database import get_db
from ...models.payment import Payment
from ...models.user import User
from ...schemas.payment import CheckoutResponse, PaymentResponse, QuickCheckoutRequest, RazorpayVerificationRequest
from ...services.checkout import create_quick_checkout, create_razorpay_checkout, create_razorpay_quick_checkout, create_test_checkout, verify_razorpay_payment, verify_test_payment

router = APIRouter()
settings = get_settings()


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def checkout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CheckoutResponse:
    payment = create_razorpay_checkout(db, current_user.id) if settings.razorpay_enabled else create_test_checkout(db, current_user.id)
    return CheckoutResponse(payment_id=payment.id, order_number=payment.order.order_number, razorpay_order_id=payment.razorpay_order_id, amount=payment.amount, currency=payment.currency, status=payment.status, test_mode=not settings.razorpay_enabled, razorpay_key_id=settings.razorpay_key_id if settings.razorpay_enabled else None)


@router.post("/quick-checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def quick_checkout(payload: QuickCheckoutRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CheckoutResponse:
    payment = create_razorpay_quick_checkout(db, current_user.id, payload.product_id, payload.quantity) if settings.razorpay_enabled else create_quick_checkout(db, current_user.id, payload.product_id, payload.quantity)
    return CheckoutResponse(payment_id=payment.id, order_number=payment.order.order_number, razorpay_order_id=payment.razorpay_order_id, amount=payment.amount, currency=payment.currency, status=payment.status, test_mode=not settings.razorpay_enabled, razorpay_key_id=settings.razorpay_key_id if settings.razorpay_enabled else None)


@router.post("/{payment_id}/verify-test", response_model=PaymentResponse)
def complete_test_payment(payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PaymentResponse:
    payment = db.scalar(select(Payment).options(selectinload(Payment.order)).where(Payment.id == payment_id, Payment.user_id == current_user.id))
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    if settings.razorpay_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test payment completion is disabled.")
    payment = verify_test_payment(db, payment)
    return PaymentResponse(payment_id=payment.id, order_number=payment.order.order_number, payment_status=payment.status, order_status=payment.order.status)


@router.post("/{payment_id}/verify", response_model=PaymentResponse)
def verify_payment(payment_id: int, payload: RazorpayVerificationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PaymentResponse:
    if not settings.razorpay_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay checkout is not enabled.")
    payment = db.scalar(select(Payment).options(selectinload(Payment.order)).where(Payment.id == payment_id, Payment.user_id == current_user.id))
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    payment = verify_razorpay_payment(db, payment, payload.razorpay_payment_id, payload.razorpay_signature)
    return PaymentResponse(payment_id=payment.id, order_number=payment.order.order_number, payment_status=payment.status, order_status=payment.order.status)
