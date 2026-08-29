from decimal import Decimal

from sqlalchemy import select

from .core.database import SessionLocal
from .models.catalog import Category, Inventory, Product


def seed_catalog() -> None:
    """Create a small local-development catalog only when it is empty."""
    db = SessionLocal()
    try:
        if db.scalar(select(Product.id).limit(1)):
            return
        electronics = Category(name="Electronics", description="Everyday technology")
        db.add(electronics)
        db.flush()
        catalog = [
            ("AstraBook Pro 14", "AI-ready laptop with 16 GB memory.", "Astra", "74999", "4.6"),
            ("WavePods Studio", "Noise-cancelling wireless headphones.", "Wave", "8999", "4.4"),
            ("Orbit Smartwatch", "Fitness and notification companion.", "Orbit", "5499", "4.3"),
        ]
        for name, description, brand, price, rating in catalog:
            product = Product(category=electronics, name=name, description=description, brand=brand, price=Decimal(price), discount=Decimal("0"), final_price=Decimal(price), rating=Decimal(rating), review_count=0)
            db.add(product)
            db.flush()
            db.add(Inventory(product_id=product.id, stock_quantity=20, reserved_quantity=0, available_quantity=20))
        db.commit()
    finally:
        db.close()
