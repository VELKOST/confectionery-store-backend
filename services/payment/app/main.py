from fastapi import FastAPI, Request
from .routes import router as payment_router
from fastapi.responses import JSONResponse

app = FastAPI(title="Payment Service")

app.include_router(payment_router, prefix="", tags=["payments"])

# Глобальный обработчик исключений для 500 ошибок
@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )
