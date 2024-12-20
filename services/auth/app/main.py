from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from .db import Base, engine
from .routes import router as auth_router

# При необходимости можно раскомментировать (но alembic миграции уже управляют схемой)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service",
    description="Микросервис авторизации для интернет-магазина кондитерских изделий",
    version="1.0.0",
)

app.include_router(auth_router, prefix="", tags=["auth"])

# Глобальный обработчик исключений для 500 ошибок
@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )
