# gateway/Dockerfile

FROM nginx:alpine

# Копируем статические файлы фронтенда в /usr/share/nginx/html/
COPY frontend/ /usr/share/nginx/html/

# Копируем конфигурацию Nginx
COPY gateway/nginx.conf /etc/nginx/nginx.conf

# Копируем SSL сертификаты
COPY gateway/ssl/ /etc/nginx/ssl/
