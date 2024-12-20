from sqlalchemy import Column, Integer, String, DateTime, text
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default="user")
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
