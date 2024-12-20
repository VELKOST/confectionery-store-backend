from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routes import router as order_router

app = FastAPI(title="Order Service")

app.include_router(order_router, prefix="", tags=["orders"])

# Глобальный обработчик исключений для 500 ошибок
@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )
