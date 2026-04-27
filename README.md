# Инструкция по запуску

## Вариант 1: С использованием Docker Compose

### Предварительные требования:
- Docker
- Docker Compose

### Запуск:

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

### Создание тестовых данных:

После запуска выполните миграцию для создания таблиц и тестовых данных:

```bash
docker-compose exec app python -m app.migrate
```

---

## Вариант 2: Без использования Docker

### Предварительные требования:
- Python 3.11+
- PostgreSQL

### Установка зависимостей:

```bash
pip install -r requirements.txt
```

### Настройка PostgreSQL:

Создайте базу данных PostgreSQL с именем `payments_db`:

```sql
CREATE DATABASE payments_db;
```

### Запуск приложения:

```bash
python -m app.main
```

Приложение будет доступно по адресу: http://localhost:8000

### Создание тестовых данных:

В другом терминале выполните миграцию:

```bash
python -m app.migrate
```

---

## Тестовые данные для входа

### Пользователь:
- **Email:** testuser@example.com
- **Password:** password123

### Администратор:
- **Email:** admin@example.com
- **Password:** admin123

---

## API Эндпоинты

### Пользователь:
- `POST /api/user/register` - Регистрация
- `POST /api/user/login` - Вход
- `GET /api/user/me` - Данные пользователя
- `GET /api/user/accounts` - Список счетов
- `GET /api/user/payments` - Список платежей

### Администратор:
- `POST /api/admin/register` - Регистрация
- `POST /api/admin/login` - Вход
- `GET /api/admin/me` - Данные администратора
- `GET /api/admin/users` - Список пользователей
- `POST /api/admin/users` - Создать пользователя
- `PUT /api/admin/users/<id>` - Обновить пользователя
- `DELETE /api/admin/users/<id>` - Удалить пользователя
- `GET /api/admin/users/<id>/accounts` - Счета пользователя

### Webhook:
- `POST /api/webhook/payment` - Обработка платежа

---

## Пример webhook запроса

```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

Signature вычисляется по формуле:
SHA256({account_id}{amount}{transaction_id}{user_id}{secret_key})

Где secret_key = gfdmhghif38yrf9ew0jkf32