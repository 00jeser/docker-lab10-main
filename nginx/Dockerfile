FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Старые www.example.com.crt/.key просрочены (до 2023) и без SAN для localhost.
# Генерируем self-signed на сборке: DNS localhost/www.example.com + 127.0.0.1.
RUN apk add --no-cache openssl \
    && mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
        -keyout /etc/nginx/ssl/localhost.key \
        -out /etc/nginx/ssl/localhost.crt \
        -subj "/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,DNS:www.example.com,IP:127.0.0.1"
