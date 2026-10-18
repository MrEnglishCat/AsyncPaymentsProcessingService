# Async Payments Processing Service

Высоконагруженный асинхронный сервис обработки платежей с гарантией доставки событий (Outbox Pattern), идемпотентностью и надежной системой уведомлений (Webhooks с Retry и Dead Letter Queue).

## 🏗 Архитектура и ключевые особенности

Проект реализован как единый асинхронный сервис на базе FastAPI, внутри которого координированно работают три компонента:

1. **API (FastAPI)**: Принимает запросы на создание платежа. Гарантирует идемпотентность через заголовок `Idempotency-Key` и уникальные ограничения в БД. Создает платеж и запись в таблице `outbox` в **одной атомарной транзакции**.
2. **Outbox Worker (Фоновая задача)**: Каждые 2 секунды опрашивает таблицу `outbox`. Использует `SELECT ... FOR UPDATE SKIP LOCKED` для безопасной конкурентной обработки и механизм `locked_until` для восстановления "зависших" задач после падения воркера.
3. **Consumer (FastStream)**: Получает события из очереди `payments.new`:
   - Эмулирует обработку платежа (2-5 сек, 90% успех / 10% ошибка).
   - Обновляет статус платежа в PostgreSQL.
   - Отправляет Webhook-уведомление клиенту через `aiohttp` (с переиспользованием сессии / Connection Pooling).
   - Реализует стратегию повторных попыток (3 попытки с задержкой 2с → 4с → 8с).
   - При исчерпании попыток сообщение автоматически маршрутизируется в **Dead Letter Queue (DLQ)**.

## 🛠 Технологический стек

- **Язык**: Python 3.12+ (совместимо с 3.14)
- **Web Framework**: FastAPI + Pydantic V2 (с вложенными настройками через `env_nested_delimiter`)
- **ORM**: SQLAlchemy 2.0 (асинхронный режим)
- **База данных**: PostgreSQL 15
- **Брокер сообщений**: RabbitMQ 4.0 + FastStream
- **Миграции**: Alembic
- **HTTP-клиент**: `aiohttp` (для высокопроизводительных webhook'ов)
- **Инфраструктура**: Docker & Docker Compose

---

## 🚀 Быстрый старт

### 1. Требования
- Установленные [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/).

### 2. Клонирование репозитория

```bash
# Клонируйте проект

git clone https://github.com/MrEnglishCat/AsyncPaymentsProcessingService.git

# Перейдите в директорию проекта 
cd AsyncPaymentsProcessingService
```

### 3. Настройка окружения
Скопируйте файл с переменными окружения:
```bash
cp .env.example .env
```
*(Файл `.env` уже содержит корректные настройки для локального запуска через Docker, включая хосты `postgres` и `rabbitmq`)*.

### 4. Запуск
Соберите и запустите все сервисы одной командой. Миграции базы данных применятся **автоматически** при старте контейнера API.
```bash
docker-compose up --build
```
*(Для запуска в фоновом режиме используйте флаг `-d`: `docker-compose up --build -d`)*

### 5. Доступные сервисы

| Сервис | URL | Учетные данные |
|--------|-----|----------------|
| **API & Swagger UI** | http://localhost:8000/docs | — |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest |
| **pgAdmin** | http://localhost:8080 | admin@admin.com / admin |

---

## 🧪 Тестирование API

### Сценарий 1: Успешная обработка платежа
Отправьте POST-запрос (замените `Idempotency-Key` на любой валидный UUID для новых тестов):

```bash
curl -X POST "http://localhost:8000/api/v1/payments/" \
  -H "X-API-Key: super-secret-test-key-123" \
  -H "Idempotency-Key: 01a1463d-1a99-7510-9e9f-7566f86f6d11" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.50,
    "currency": "RUB",
    "description": "Оплата заказа №123",
    "meta": {"order_id": "123"},
    "webhook_url": "https://httpbin.org/post"
  }'
```
**Ожидаемый результат:** `202 Accepted`. В логах контейнера `payments_api` вы увидите цепочку: создание в БД → публикация в Outbox → обработка консюмером → успешная доставка Webhook.

### Сценарий 2: Проверка идемпотентности
Повторите запрос выше с **тем же самым** `Idempotency-Key`:
- Если данные идентичны → вернется существующий платеж (`202 Accepted`).
- Если изменить `amount` или `currency` при том же ключе → вернется `409 Conflict`.

### Сценарий 3: Тестирование Dead Letter Queue (DLQ)
Чтобы проверить механизм отказоустойчивости, создайте платеж с заведомо нерабочим URL:

```bash
curl -X POST "http://localhost:8000/api/v1/payments/" \
  -H "X-API-Key: super-secret-test-key-123" \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "currency": "RUB",
    "description": "Test DLQ Flow",
    "webhook_url": "http://invalid-url-that-does-not-exist.test"
  }'
```
**Что произойдет:**
1. Consumer попытается отправить webhook 3 раза с экспоненциальной задержкой (2с, 4с, 8с).
2. После 3-й неудачи будет выброшено исключение, и FastStream сделает `nack` без `requeue`.
3. RabbitMQ автоматически переместит сообщение в очередь `payments.new.dlq`.
4. **Проверка:** Откройте RabbitMQ UI (http://localhost:15672) → вкладка **Queues** → `payments.new.dlq`. Там будет находиться 1 сообщение.

---

## 📁 Структура проекта

```text
.
├── app/
│   ├── api/              # Эндпоинты FastAPI
│   ├── broker/           # Конфигурация RabbitMQ и FastStream
│   ├── config/           # Pydantic settings (централизованная конфигурация)
│   ├── consumers/        # Обработчики событий из очереди
│   ├── dependencies/     # Зависимости (сессии БД, сервисы)
│   ├── enums/            # Перечисления (статусы, валюты)
│   ├── exceptions/       # Исключения и обработчики исключений
│   ├── migrations/       # Alembic миграции
│   ├── models/           # SQLAlchemy модели
│   ├── outbox/           # OutboxProducer
│   ├── repository/       # Репозитории (Data Access Layer)
│   ├── schemas/          # Pydantic схемы валидации
│   ├── services/         # Бизнес-логика (Webhook retry, платежи)
│   └── utils/            # Бизнес-логика (Webhook retry, платежи)
│   
├── .env.example          # Шаблон переменных окружения
├── .gitignore            # Файл git
├── alembic.ini           # Конфигурация Alembic
├── docker-compose.yml    # Оркестрация контейнеров
├── Dockerfile            # Инструкции сборки образа backend (FastAPI)
├── main.py               # Точка входа, управление жизненным циклом (lifespan)
├── README.md             # Описание проекта
└── requirements.txt      # Зависимости Python
```

---

## 💡 Архитектурные решения и заметки

1. **Единый контейнер**: Для упрощения развертывания в рамках задания API, Outbox Worker и Consumer работают в одном процессе. Это легко масштабируется: для разделения достаточно вынести запуск воркера и `broker.include_router()` в отдельные entry-point скрипты и добавить их как отдельные сервисы в `docker-compose.yml`.
2. **Генерация UUID**: В моделях можно использовать `server_default=text("gen_random_uuid()")`, так как это нативная и наиболее производительная функция PostgreSQL (в отличие от кастомных `uuidv7`, требующих расширений). Эта часть кода закоментирована. 
3. **Совместимость с Windows**: В файлы `main.py` и `migrations/env.py` добавлена политика `asyncio.WindowsSelectorEventLoopPolicy`. Это для корректной работы асинхронного `psycopg` и `alembic` при локальной разработке на ОС Windows, при этом в Linux/Docker этот код игнорируется.
4. **Безопасность Webhook**: Используется ленивая инициализация `aiohttp.ClientSession` с переиспользованием TCP-соединений (Connection Pooling), что критически важно для производительности при массовых рассылках.

---

## 🔧 Локальная разработка (без Docker)

Если вы хотите запустить проект напрямую на хост-машине:

```bash
# 0. Клонируйте проект

git clone https://github.com/MrEnglishCat/AsyncPaymentsProcessingService.git

# Перейдите в директорию проекта 
cd AsyncPaymentsProcessingService


# 1. Создайте виртуальное окружение и установите зависимости
python -m venv .venv
source .venv/Scripts/activate  # Для Windows
pip install -r requirements.txt

# 2. Убедитесь, что в .env указаны хосты localhost:
# db__HOST="localhost"
# rabbit__HOST="localhost"
# rabbit__URL="amqp://guest:guest@localhost:5672/"

# 3. Запустите инфраструктуру
docker-compose up -d postgres rabbitmq

# 4. Примените миграции
python -m alembic upgrade head

# 5. Запустите приложение
uvicorn app.main:app --reload
```