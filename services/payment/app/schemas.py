from pydantic import BaseModel, confloat
from typing import Optional
from datetime import datetime


class PaymentCreateRequest(BaseModel):
    order_id: int
    amount: confloat(gt=0)
    payment_method: str


class PaymentResponse(BaseModel):
    payment_id: int
    status: str
    amount: float
    created_at: datetime

    class Config:
        orm_mode = True


class CreatePaymentResponse(BaseModel):
    payment_id: int
    status: str
    message: str
