from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...core.database import get_db
from ...models.catalog import Product
from ...schemas.catalog import ProductRead

router = APIRouter()


@router.get("", response_model=list[ProductRead])
def list_products(
    query: str | None = Query(default=None, min_length=1, max_length=100),
    category_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> list[Product]:
    statement = select(Product).options(selectinload(Product.category)).where(Product.is_active == True)  # noqa: E712
    if query:
        statement = statement.where(Product.name.ilike(f"%{query.strip()}%"))
    if category_id:
        statement = statement.where(Product.category_id == category_id)
    return list(db.scalars(statement.order_by(Product.created_at.desc())).all())
