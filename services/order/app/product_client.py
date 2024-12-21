# order/product_client.py
import os
import requests
from fastapi import HTTPException, status

from datetime import datetime, timedelta, timezone
from jose import jwt
import logging

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product:8000")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Проверка наличия необходимых переменных окружения
if not JWT_SECRET or not JWT_ALGORITHM:
    logger.error("JWT_SECRET_KEY и JWT_ALGORITHM должны быть установлены в переменных окружения.")
    raise Exception("Missing JWT configuration.")

# Кэширование токена и времени его истечения
_service_token = None
_token_expiry = None

def create_service_token():
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "sub": "service_account",
        "role": "admin",
        "user_id": 0,
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"Создан новый сервисный токен, истекает в {expire.isoformat()}")
    return token, expire

def get_service_token():
    global _service_token, _token_expiry
    if _service_token is None or datetime.now(timezone.utc) >= _token_expiry:
        _service_token, _token_expiry = create_service_token()
    return _service_token

def get_product_info(product_id: int):
    """
    Получает информацию о продукте по его ID из Product Service.

    :param product_id: ID продукта
    :return: Словарь с информацией о продукте
    """
    headers = {"Authorization": f"Bearer {get_service_token()}"}
    params = {"product_id": product_id}

    try:
        resp = requests.get(f"{PRODUCT_SERVICE_URL}/products", params=params, headers=headers, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - Status Code: {resp.status_code}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve product info")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception: {req_err}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Product service is unavailable")

    try:
        products = resp.json()
    except ValueError:
        logger.error("Invalid JSON response from Product Service")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid response from product service")

    if not isinstance(products, list):
        logger.error(f"Unexpected response format: {products}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected response format from product service")

    if not products:
        logger.warning(f"Product with id {product_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")

    product = products[0]

    # Проверка наличия необходимых полей
    required_fields = ["id", "name", "price", "category", "seller_id"]
    missing_fields = [field for field in required_fields if field not in product]
    if missing_fields:
        logger.error(f"Missing fields {missing_fields} in product data")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incomplete product data received")

    return product
