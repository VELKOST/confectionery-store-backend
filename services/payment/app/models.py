from sqlalchemy import Column, Integer, String, Float, DateTime, text
from .db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default='pending')  # pending, success, failed
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
