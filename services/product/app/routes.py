from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from .db import get_db
from .models import Product
from .schemas import ProductCreate, ProductResponse, ProductUpdate, MessageResponse
from .security import get_current_user_token

router = APIRouter()


@router.get("/products", response_model=List[ProductResponse])
def get_products(
        category: Optional[str] = Query(None),
        price_min: Optional[float] = Query(None),
        price_max: Optional[float] = Query(None),
        product_id: Optional[int] = Query(None),  # добавили параметр
        db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if price_min is not None:
        if price_min < 0:
            raise HTTPException(status_code=400, detail="price_min must be >= 0")
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        if price_max < 0:
            raise HTTPException(status_code=400, detail="price_max must be >= 0")
        query = query.filter(Product.price <= price_max)
    if product_id is not None:
        query = query.filter(Product.id == product_id)

    products = query.all()
    return products


@router.post("/products", response_model=MessageResponse)
def create_product(
        product_data: ProductCreate,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(status_code=401, detail="Only sellers or admins can add products")

    # Если нужно строго доверять seller_id из токена, уберём seller_id из body и возьмём его из токена:
    # Но у нас его нет, есть только user_id. Предположим, что user_id = seller_id.
    # Тогда игнорируем product_data.seller_id, а берём user["user_id"].
    # Это более надёжный вариант, чтобы не подменяли seller_id.
    seller_id = user["user_id"]

    if not product_data.name or product_data.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid product data")

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        seller_id=seller_id  # берём из токена
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product added successfully"}


@router.put("/products/{product_id}", response_model=MessageResponse)
def update_product(
        product_id: int,
        product_update: ProductUpdate,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(status_code=401, detail="Only sellers or admins can update products")

    # Если seller - проверяем, что товар принадлежит этому seller_id (из user_id)
    if user["role"] == "seller" and product.seller_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="You cannot update products not owned by you")

    if product_update.name:
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.price is not None:
        if product_update.price <= 0:
            raise HTTPException(status_code=400, detail="Invalid price")
        product.price = product_update.price
    if product_update.category is not None:
        product.category = product_update.category

    db.commit()
    return {"message": "Product updated successfully"}


@router.delete("/products/{product_id}", response_model=MessageResponse)
def delete_product(
        product_id: int,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(status_code=401, detail="Only sellers or admins can delete products")

    # Если seller - проверяем, что товар принадлежит этому пользователю
    if user["role"] == "seller" and product.seller_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="You cannot delete products not owned by you")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
