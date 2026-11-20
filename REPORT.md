# Итоговый отчёт: исправления Docker Compose (лаб. №10)

## 1. Неверный проброс порта nginx

- **Симптом:** `https://localhost` недоступен; внутри контейнера слушается 443, с хоста опубликован другой порт.
- **Файл:** `docker-compose.yml`
- **Исправление:** `445:445` заменён на `443:443`.

## 2. неверное имя upstream

- **Симптом:** nginx не проксирует запросы на бэкенды.
- **Файл:** `nginx/nginx.conf`
- **Исправление:** `proxy_pass http://app` заменён на `proxy_pass http://loadbalancer` (имя блока `upstream`).

## 3. Неверные порты бэкендов в upstream

- **Симптом:** 502 Bad Gateway — nginx стучится на порт 81.
- **Файл:** `nginx/nginx.conf`
- **Исправление:** `app1:81` / `app2:81` → `app1:8080` / `app2:8080` (оба Flask слушают 8080).

## 4. Алгоритм `least_conn` вместо round-robin

- **Симптом:** при равной нагрузке нет явного чередования app1/app2 при обновлении страницы.
- **Файл:** `nginx/nginx.conf`
- **Исправление:** директива `least_conn` удалена; используется round-robin по умолчанию.

## 5. Много worker-процессов и ранний старт nginx

- **Симптом:** даже при round-robin подряд идут ответы только от app1 (у каждого worker свой счётчик; бэкенд, ещё не готовый при старте, временно выпадает из пула).
- **Файлы:** `nginx/nginx.main.conf`, `nginx/Dockerfile`, `nginx/nginx.conf`, `docker-compose.yml`
- **Исправление:** `worker_processes 1` в главном конфиге; у серверов upstream `max_fails=0`; healthcheck у app1/app2 и `depends_on: condition: service_healthy` для nginx.

## 6. `server_name` без localhost

- **Симптом:** имя из задания (`localhost`) не совпадало с конфигом (www.example.com).
- **Файл:** `nginx/nginx.conf`
- **Исправление:** `server_name localhost www.example.com`.

## 7. Сертификаты отсутствовали в образе и были просрочены

- **Симптом:** nginx не стартует (нет файлов по путям) либо браузер отклоняет просроченный сертификат без SAN для localhost.
- **Файлы:** `nginx/Dockerfile`, `nginx/nginx.conf`
- **Исправление:** так как в задании написано `После перехода по адресу https://localhost и подтверждения самоподписанного сертификата`, предпологаю, что необходимы всеже самоподписанные сертификаты на localhost, а не example.com, плюс старые www.example.com.crt/.key просрочены (до 2023), поэтому на этапе сборки генерируется self-signed сертификат в `/etc/nginx/ssl/` с SAN `DNS:localhost`, `DNS:www.example.com`, `IP:127.0.0.1`. В конфиге указаны абсолютные пути. Старые `www.example.com.crt` / `.key` не используются. 

## 8. Устаревшие протоколы TLS

- **Симптом:** на `nginx:alpine` (OpenSSL 3) связка TLSv1/TLSv1.1 и старых ciphers часто ломает старт.
- **Файл:** `nginx/nginx.conf`
- **Исправление:** `ssl_protocols TLSv1.2 TLSv1.3`.

## 9. Flask отвечает на `/hello`, а не на `/`

- **Симптом:** `https://localhost/` даёт 404.
- **Файлы:** `app1/app1.py`, `app2/app2.py`
- **Исправление:** маршрут изменён на `@app.route('/')`.

## 10. Неверный каталог шаблонов

- **Симптом:** `TemplateNotFound: index.html` — том смонтирован в `/storage`, Flask ищет `/templates`.
- **Файлы:** `app1/app1.py`, `app2/app2.py`
- **Исправление:** `Flask(__name__, template_folder='/storage')`.

## 11. app2 не передаёт `source_app`

- **Симптом:** текст «Hello World from !» без имени приложения.
- **Файл:** `app2/app2.py`
- **Исправление:** `render_template('index.html', source_app='app2')`.

## 12. app2 слушает привилегированный порт 80

- **Симптом:** Permission denied при старте от пользователя `www`.
- **Файл:** `app2/app2.py`
- **Исправление:** порт изменён на `8080` (как у app1).

## 13. Неверный CMD в образе app2

- **Симптом:** контейнер app2 падает — запускается несуществующий `app1.py`.
- **Файл:** `app2/Dockerfile`
- **Исправление:** `CMD [ "app2.py" ]`.

## 14. Несовместимые версии Flask / Werkzeug с Python 3.12

- **Симптом:** установка или запуск на `python:3.12-alpine` с Flask 2.2.2 / Werkzeug 2.2.2.
- **Файлы:** `app1/requirements.txt`, `app2/requirements.txt`
- **Исправление:** `Flask==3.0.3`, `Werkzeug==3.0.3`.

## 15. Сломанный HTML-тег в шаблоне

- **Симптом:** некорректная разметка, не соответствует скриншоту с `<h1>`.
- **Файл:** `storage/index.html`
- **Исправление:** `</h1>...` заменён на `<h1>Hello World from {{ source_app }}!</h1>`.

## Результат

После `docker compose build` и `docker compose up` обращение к `https://localhost` (с подтверждением самоподписанного сертификата) поочерёдно возвращает контент от app1 и app2.
