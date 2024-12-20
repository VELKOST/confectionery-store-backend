import os
import requests
from fastapi import HTTPException, status
from datetime import datetime, timedelta, UTC
from jose import jwt

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order:8000")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def create_service_token():
    expire = datetime.now(UTC) + timedelta(hours=1)
    payload = {
        "sub": "service_account",
        "role": "admin",
        "user_id": 0,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


SERVICE_TOKEN = create_service_token()


def get_order_info(order_id: int):
    headers = {"Authorization": f"Bearer {SERVICE_TOKEN}"}
    resp = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}", headers=headers, timeout=5)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Order not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve order info")
    return resp.json()
