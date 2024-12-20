from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db import get_db
from .models import Payment
from .schemas import PaymentCreateRequest, CreatePaymentResponse, PaymentResponse
from .security import get_current_user_token
from .order_client import get_order_info
from .rabbitmq import publish_payment_status

router = APIRouter()


@router.post("/payments", response_model=CreatePaymentResponse)
def create_payment(
        payment_data: PaymentCreateRequest,
        user=Depends(get_current_user_token),
        db: Session = Depends(get_db)
):
    # Проверяем роль: user или admin
    if user["role"] not in ["user", "admin"]:
        raise HTTPException(status_code=401, detail="Only users or admins can create payments")

    # Проверяем заказ
    order_info = get_order_info(payment_data.order_id)
    # order_info содержит поля: order_id, user_id, total_price, status, items[]
    if user["role"] == "user" and order_info["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="You cannot pay for orders not belonging to you")

    # Проверим сумму
    if abs(order_info["total_price"] - payment_data.amount) > 0.0001:
        raise HTTPException(status_code=400, detail="Payment amount does not match order total price")

    # Проверим статус заказа - должен быть оплачен, допустим, если статус "created" или "in_progress"
    # можно оплатить. Если статус "delivered" или "cancelled", то нет смысла оплачивать.
    if order_info["status"] not in ["created", "in_progress"]:
        raise HTTPException(status_code=400, detail="Order cannot be paid in its current status")

    # Создаём платёж (pending)
    new_payment = Payment(
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        status="pending"
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Имитируем процесс оплаты
    # Допустим, оплата всегда успешна для демонстрации
    new_payment.status = "success"
    db.commit()

    # Отправляем сообщение о статусе платежа в RabbitMQ
    publish_payment_status({
        "payment_id": new_payment.id,
        "order_id": new_payment.order_id,
        "status": new_payment.status,
        "amount": new_payment.amount
    })

    return {
        "payment_id": new_payment.id,
        "status": new_payment.status,
        "message": "Payment initiated successfully"
    }


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, user=Depends(get_current_user_token), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentResponse(
        payment_id=payment.id,
        status=payment.status,
        amount=payment.amount,
        created_at=payment.created_at
    )
