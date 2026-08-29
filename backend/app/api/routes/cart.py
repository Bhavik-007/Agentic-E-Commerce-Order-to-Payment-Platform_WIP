from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...api.deps import get_current_user
from ...core.database import get_db
from ...models.cart import Cart, CartItem
from ...models.catalog import Product
from ...models.user import User
from ...schemas.cart import CartItemRead, CartItemRequest, CartRead

router = APIRouter()


def get_open_cart(db: Session, user_id: int) -> Cart:
    cart = db.scalar(select(Cart).options(selectinload(Cart.items).selectinload(CartItem.product)).where(Cart.user_id == user_id, Cart.status == "OPEN"))
    if cart:
        return cart
    cart = Cart(user_id=user_id)
    db.add(cart)
    db.flush()
    return cart


def cart_response(cart: Cart) -> CartRead:
    items = [
        CartItemRead(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.unit_price * item.quantity,
        )
        for item in cart.items
    ]
    return CartRead(id=cart.id, items=items, subtotal=sum((item.line_total for item in items), Decimal("0")))


@router.get("", response_model=CartRead)
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartRead:
    return cart_response(get_open_cart(db, current_user.id))


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def add_item(payload: CartItemRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartRead:
    product = db.scalar(select(Product).where(Product.id == payload.product_id, Product.is_active == True))  # noqa: E712
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    cart = get_open_cart(db, current_user.id)
    item = next((cart_item for cart_item in cart.items if cart_item.product_id == product.id), None)
    if item:
        item.quantity += payload.quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product.id, quantity=payload.quantity, unit_price=product.final_price, product=product)
        cart.items.append(item)
    db.commit()
    db.refresh(cart)
    return cart_response(get_open_cart(db, current_user.id))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    cart = get_open_cart(db, current_user.id)
    item = next((cart_item for cart_item in cart.items if cart_item.id == item_id), None)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found.")
    db.delete(item)
    db.commit()
