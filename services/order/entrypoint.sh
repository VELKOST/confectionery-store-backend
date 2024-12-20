#!/bin/sh

# Ожидание готовности базы данных и RabbitMQ
./wait-for-it.sh auth_db:5432 --timeout=30 --strict -- echo "Database is up"
./wait-for-it.sh rabbitmq:5672 --timeout=30 --strict -- echo "RabbitMQ is up"

# Применение миграций Alembic
alembic upgrade head

# Запуск приложения
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
