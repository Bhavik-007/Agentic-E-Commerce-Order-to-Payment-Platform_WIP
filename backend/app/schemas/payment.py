from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field


class CheckoutResponse(BaseModel):
    payment_id: int
    order_number: str
    razorpay_order_id: str
    amount: Decimal
    currency: str
    status: str
    test_mode: bool
    razorpay_key_id: str | None = None


class PaymentResponse(BaseModel):
    payment_id: int
    order_number: str
    payment_status: str
    order_status: str


class QuickCheckoutRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=5)


class RazorpayVerificationRequest(BaseModel):
    razorpay_payment_id: str = Field(min_length=1, max_length=100)
    razorpay_signature: str = Field(min_length=1, max_length=255)
