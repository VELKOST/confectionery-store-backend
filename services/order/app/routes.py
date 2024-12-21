# order/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .db import get_db
from .models import Order, OrderItem
from .schemas import (
    OrderCreateRequest, CreateOrderResponse, OrderListItem,
    OrderResponse, OrderStatusUpdateRequest, MessageResponse, OrderItemResponse
)
from .security import get_current_user_token
from .product_client import get_product_info
from .rabbitmq import publish_order_created

router = APIRouter()


@router.get("/orders/me", response_model=List[OrderListItem])
def get_orders_for_user(user=Depends(get_current_user_token), db: Session = Depends(get_db)):
    """
    Эндпоинт для получения заказов текущего пользователя.
    """
    orders = db.query(Order).filter(Order.user_id == user["user_id"]).all()

    # Создаём вручную объекты OrderListItem
    order_list = [
        OrderListItem(
            order_id=order.id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at
        )
        for order in orders
    ]

    return order_list


@router.post("/orders", response_model=CreateOrderResponse)
def create_order(
        order_data: OrderCreateRequest,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    # Проверяем, что user либо admin, либо пользователь, создающий заказ для себя
    if user["role"] not in ["admin", "user"]:
        raise HTTPException(status_code=401, detail="Only users or admins can create orders")

    if user["role"] == "user" and user["user_id"] != order_data.user_id:
        raise HTTPException(status_code=403, detail="You can only create orders for yourself")

    # Проверяем товары
    total_calculated = 0.0
    items_to_insert = []
    for item in order_data.items:
        product = get_product_info(item.product_id)
        # product = { "id":..., "name":..., "price":..., "category":..., "seller_id":... }
        line_price = product["price"] * item.quantity
        total_calculated += line_price
        items_to_insert.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity,
            "price": product["price"]
        })

    # Сравниваем total_price
    if abs(total_calculated - order_data.total_price) > 0.0001:
        raise HTTPException(status_code=400, detail="Total price does not match calculated price")

    new_order = Order(
        user_id=order_data.user_id,
        status="created",
        total_price=total_calculated
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Добавляем позиции заказа
    for i in items_to_insert:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=i["product_id"],
            product_name=i["product_name"],
            quantity=i["quantity"],
            price=i["price"]
        )
        db.add(order_item)
    db.commit()

    # Отправляем сообщение в RabbitMQ о новом заказе
    publish_order_created({
        "order_id": new_order.id,
        "user_id": new_order.user_id,
        "total_price": new_order.total_price,
        "status": new_order.status,
        "items": [{"product_id": x.product_id, "quantity": x.quantity, "price": x.price} for x in new_order.items]
    })

    return {"order_id": new_order.id, "message": "Order created successfully"}


@router.get("/orders", response_model=List[OrderListItem])
def list_orders(
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка заказов.
    - Для `admin` возвращает все заказы.
    - Для `seller` возвращает заказы, содержащие их продукты.
    """
    if user["role"] == "admin":
        orders = db.query(Order).all()
    elif user["role"] == "seller":
        seller_id = user["user_id"]
        # Получаем все заказы
        all_orders = db.query(Order).all()
        filtered_orders = []
        seen_order_ids = set()
        for order in all_orders:
            if order.id in seen_order_ids:
                continue  # Уже добавлен
            for item in order.items:
                try:
                    product_info = get_product_info(item.product_id)
                    if product_info.get("seller_id") == seller_id:
                        filtered_orders.append(order)
                        seen_order_ids.add(order.id)
                        break  # Не нужно проверять остальные товары в этом заказе
                except HTTPException as e:
                    # Логировать ошибку и продолжить
                    logger.error(f"Error fetching product info for product_id {item.product_id}: {e.detail}")
                    continue
        orders = filtered_orders
    else:
        raise HTTPException(status_code=401, detail="Only admin and seller can view orders")

    # Создаём список OrderListItem
    order_list = [
        OrderListItem(
            order_id=order.id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at
        )
        for order in orders
    ]

    return order_list


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
        order_id: int,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Если user - может видеть только свои заказы
    if user["role"] == "user" and order.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="You cannot view this order")

    # Если user - seller, проверить, что заказ содержит их продукты
    if user["role"] == "seller":
        has_own_product = False
        for item in order.items:
            try:
                product_info = get_product_info(item.product_id)
                if product_info.get("seller_id") == user["user_id"]:
                    has_own_product = True
                    break
            except HTTPException as e:
                # Логировать ошибку и продолжить
                logger.error(f"Error fetching product info for product_id {item.product_id}: {e.detail}")
                continue
        if not has_own_product:
            raise HTTPException(status_code=403, detail="You cannot view this order")

    # admin может видеть любой заказ
    # 'user' может видеть только свои заказы
    # 'seller' может видеть заказы с их продуктами

    items = []
    for i in order.items:
        items.append(OrderItemResponse(
            product_id=i.product_id,
            name=i.product_name,
            quantity=i.quantity,
            price=i.price
        ))

    return OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_price=order.total_price,
        created_at=order.created_at,
        items=items
    )


@router.put("/orders/{order_id}/status", response_model=MessageResponse)
def update_order_status(
        order_id: int,
        status_data: OrderStatusUpdateRequest,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    # Только admin может обновлять статус
    if user["role"] != "admin":
        raise HTTPException(status_code=401, detail="Only admin can update order status")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if status_data.status not in ["created", "in_progress", "ready", "delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid order status")

    order.status = status_data.status
    db.commit()
    return {"message": "Order status updated successfully"}
