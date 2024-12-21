from pydantic import BaseModel, confloat
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: confloat(gt=0)  # цена должна быть > 0
    category: Optional[str] = None


class ProductCreate(ProductBase):
    seller_id: int


class ProductUpdate(ProductBase):
    pass


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    seller_id: int

    class Config:
        orm_mode = True


class MessageResponse(BaseModel):
    message: str
