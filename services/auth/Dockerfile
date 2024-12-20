FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini alembic.ini

# Копируем wait-for-it.sh
COPY wait-for-it.sh .
COPY entrypoint.sh .
RUN chmod +x wait-for-it.sh entrypoint.sh
# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

# Определяем точку входа
ENTRYPOINT ["./entrypoint.sh"]
## Запускаем приложение после ожидания готовности auth_db и rabbitmq
#CMD ["./wait-for-it.sh", "auth_db:5432", "--", "./wait-for-it.sh", "rabbitmq:5672", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]