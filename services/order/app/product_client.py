import os
import requests
from fastapi import HTTPException, status

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product:8000")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Предположим, что нам нужен авторизованный запрос к Product Service.
# У нас есть токен пользователя. Для доверенности стоит вызвать Product service
# под ролью admin или доверенным сервисным аккаунтом. Для упрощения создадим сервисный токен.
# В реальном проекте надо либо иметь сервисный аккаунт (client_credentials), либо прокидывать токен admin.
# Здесь мы просто используем тот же секрет и генерируем специальный токен для межсервисной коммуникации.
# Считаем, что Product service доверяет токену, подписанному тем же секретным ключом.
# (В идеале нужен отдельный сервис Auth для сервисных токенов.)

from datetime import datetime, timedelta, UTC
from jose import jwt

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

def get_product_info(product_id: int):
    headers = {"Authorization": f"Bearer {SERVICE_TOKEN}"}
    # Предположим, что Product Service имеет эндпоинт GET /products?product_id=<id> для получения конкретного товара.
    # Если нет, придется получать полный список и фильтровать. Добавим такой эндпоинт в Product Service.
    # Если нужно изменить Product Service - добавим поддержку фильтрации по product_id.
    # (Представим, что мы уже дописали Product Service: GET /products?product_id=<id> возвращает массив из 0 или 1 товара.)

    resp = requests.get(f"{PRODUCT_SERVICE_URL}/products?product_id={product_id}", headers=headers, timeout=5)
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve product info")
    products = resp.json()
    if not products or len(products) == 0:
        # товар не найден
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product {product_id} not found")
    product = products[0]
    return product
