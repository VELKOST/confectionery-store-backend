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

ENTRYPOINT ["./entrypoint.sh"]
# Выполняем миграции при старте контейнера:
#CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000