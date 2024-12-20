from pydantic import BaseModel, conint, confloat
from typing import List, Optional
from datetime import datetime


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: conint(gt=0)


class OrderCreateRequest(BaseModel):
    user_id: int
    items: List[OrderItemRequest]
    total_price: confloat(gt=0)


class OrderItemResponse(BaseModel):
    product_id: int
    name: str
    quantity: int
    price: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    status: str
    total_price: float
    items: List[OrderItemResponse]
    created_at: datetime


class OrderListItem(BaseModel):
    order_id: int
    status: str
    total_price: float
    created_at: datetime

    class Config:
        orm_mode = True

class OrderStatusUpdateRequest(BaseModel):
    status: str


class CreateOrderResponse(BaseModel):
    order_id: int
    message: str


class MessageResponse(BaseModel):
    message: str
