from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=20)


class CartItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class CartRead(BaseModel):
    id: int
    items: list[CartItemRead]
    subtotal: Decimal
