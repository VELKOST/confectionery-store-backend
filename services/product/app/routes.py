# product/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from .db import get_db
from .models import Product
from .schemas import ProductCreate, ProductResponse, ProductUpdate, MessageResponse
from .security import get_current_user_token

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def get_products(
        category: Optional[str] = Query(None, description="Фильтр по категории"),
        price_min: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
        price_max: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
        product_id: Optional[int] = Query(None, description="ID продукта для получения конкретного товара"),
        db: Session = Depends(get_db),
        user=Depends(get_current_user_token)  # Добавьте эту зависимость, если требуется аутентификация
):
    """
    Получает список продуктов с возможностью фильтрации.
    Если указан `product_id`, возвращает продукт с этим ID.
    """
    if user["role"] not in ["admin", "seller", "user"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для доступа к этому ресурсу.")

    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    if price_min is not None:
        query = query.filter(Product.price >= price_min)

    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    if product_id is not None:
        query = query.filter(Product.id == product_id)

    products = query.all()

    if product_id is not None and not products:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    return products


@router.post("/", response_model=MessageResponse)
def create_product(
        product_data: ProductCreate,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    """
    Создаёт новый продукт.
    Доступно только для пользователей с ролью `seller` или `admin`.
    """
    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для добавления продуктов")

    seller_id = user["user_id"]

    # Дополнительная валидация данных
    if not product_data.name or product_data.price <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверные данные продукта")

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        seller_id=seller_id  # Берём из токена пользователя
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Продукт успешно добавлен"}


@router.put("/{product_id}", response_model=MessageResponse)
def update_product(
        product_id: int,
        product_update: ProductUpdate,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    """
    Обновляет существующий продукт.
    Доступно только для пользователей с ролью `seller` или `admin`.
    Продавец может обновлять только свои продукты.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Продукт не найден")

    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для обновления продуктов")

    # Если пользователь с ролью `seller`, проверяем принадлежность продукта
    if user["role"] == "seller" and product.seller_id != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Вы не можете обновлять продукты, принадлежащие другим пользователям")

    # Обновление полей продукта
    if product_update.name is not None:
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.price is not None:
        if product_update.price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Цена должна быть положительной")
        product.price = product_update.price
    if product_update.category is not None:
        product.category = product_update.category

    db.commit()

    return {"message": "Продукт успешно обновлён"}


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
        product_id: int,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    """
    Удаляет существующий продукт.
    Доступно только для пользователей с ролью `seller` или `admin`.
    Продавец может удалять только свои продукты.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Продукт не найден")

    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для удаления продуктов")

    # Если пользователь с ролью `seller`, проверяем принадлежность продукта
    if user["role"] == "seller" and product.seller_id != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Вы не можете удалять продукты, принадлежащие другим пользователям")

    db.delete(product)
    db.commit()

    return {"message": "Продукт успешно удалён"}
