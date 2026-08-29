from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models.catalog import Product


def product_payload(product: Product) -> dict[str, object]:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "brand": product.brand,
        "price": str(product.final_price),
        "currency": product.currency,
        "rating": str(product.rating) if product.rating is not None else None,
        "category": product.category.name,
    }


def search_products(db: Session, query: str | None = None, limit: int = 5) -> list[dict[str, object]]:
    statement = select(Product).options(selectinload(Product.category)).where(Product.is_active == True)  # noqa: E712
    if query:
        statement = statement.where(Product.name.ilike(f"%{query.strip()}%"))
    products = db.scalars(statement.order_by(Product.rating.desc()).limit(min(max(limit, 1), 20))).all()
    return [product_payload(product) for product in products]


def get_product(db: Session, product_id: int) -> dict[str, object] | None:
    product = db.scalar(select(Product).options(selectinload(Product.category)).where(Product.id == product_id, Product.is_active == True))  # noqa: E712
    return product_payload(product) if product else None
