from fastapi import APIRouter

from .routes import assistant, auth, cart, health, payments, products

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["agent supervisor"])
api_router.include_router(payments.router, prefix="/payments", tags=["test payments"])
