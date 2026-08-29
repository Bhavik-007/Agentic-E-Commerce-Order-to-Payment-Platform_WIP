"""Local smoke test for the dummy Razorpay-style payment workflow."""

from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.main import app

email = f"payment-test-{uuid4().hex[:10]}@example.com"

with TestClient(app) as client:
    registration = client.post("/api/v1/auth/register", json={"first_name": "Payment", "last_name": "Tester", "email": email, "password": "test-password-123"})
    registration.raise_for_status()
    token = registration.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    products = client.get("/api/v1/products").json()
    assert products, "Expected seeded demo products."
    client.post("/api/v1/cart/items", headers=headers, json={"product_id": products[0]["id"], "quantity": 1}).raise_for_status()
    checkout = client.post("/api/v1/payments/checkout", headers=headers)
    checkout.raise_for_status()
    payment = checkout.json()
    verified = client.post(f"/api/v1/payments/{payment['payment_id']}/verify-test", headers=headers)
    verified.raise_for_status()
    quick_checkout = client.post("/api/v1/payments/quick-checkout", headers=headers, json={"product_id": products[0]["id"], "quantity": 1})
    quick_checkout.raise_for_status()
    quick_verified = client.post(f"/api/v1/payments/{quick_checkout.json()['payment_id']}/verify-test", headers=headers)
    quick_verified.raise_for_status()
    print({"cart_order": payment["order_number"], "cart_payment": verified.json()["payment_status"], "quick_order": quick_checkout.json()["order_number"], "quick_payment": quick_verified.json()["payment_status"]})
