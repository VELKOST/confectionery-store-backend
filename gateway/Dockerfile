# gateway/Dockerfile

# Используем официальный образ Nginx на базе Alpine Linux
FROM nginx:1.23-alpine

# Удаляем стандартную конфигурацию Nginx
RUN rm /etc/nginx/conf.d/default.conf


# Устанавливаем рабочую директорию
WORKDIR /usr/share/nginx/html

# Копируем статические файлы фронтенда в директорию Nginx
COPY html/ /usr/share/nginx/html/


# Копируем свою конфигурацию Nginx в контейнер
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем SSL сертификаты
COPY ssl /etc/nginx/ssl


# Устанавливаем права доступа (опционально, если необходимо)
# RUN chmod -R 755 /usr/share/nginx/html

# Открываем порты 80 (HTTP) и 443 (HTTPS)
EXPOSE 80 443

# Запускаем Nginx в фоновом режиме
CMD ["nginx", "-g", "daemon off;"]
