from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    brand: str | None
    final_price: Decimal
    currency: str
    image_url: str | None
    rating: Decimal | None
    review_count: int
    category: CategoryRead
