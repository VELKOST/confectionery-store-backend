from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routes import router as product_router

# Alembic управляет схемой, поэтому здесь create_all не нужен
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Service")

# Настройка CORS
origins = [
    "https://localhost",
    "http://localhost",
    # Добавьте другие разрешённые источники при необходимости
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешённые источники
    allow_credentials=True,
    allow_methods=["*"],      # Разрешённые HTTP методы
    allow_headers=["*"],      # Разрешённые заголовки
)
app.include_router(product_router, prefix="/products", tags=["products"])

# Глобальный обработчик исключений для 500 ошибок
@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )
