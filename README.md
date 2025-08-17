# Сайт Terrasite

Сайт для команды Terrasite с формой заявок.

## Технологии

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python FastAPI (асинхронный)
- **База данных**: JSON файл
- **Email**: SMTP через Yandex (асинхронно)
- **Тестирование**: pytest, AsyncMock
- **Валидация**: Pydantic v2

## Установка и запуск

### 1. Создайте виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# или source venv/bin/activate  # Linux/Mac
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте email конфигурацию

Создайте файл `.env` или установите переменные окружения:

```bash
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=465
SMTP_USER=team.terrasite@yandex.ru
SMTP_PASSWORD=your-app-password
FROM_EMAIL=team.terrasite@yandex.ru
TO_EMAIL=notifications@domain.com
```

### 4. Запустите сервер

```bash
python main.py
# или
uvicorn main:app --reload
```

Сайт будет доступен по адресу: http://localhost:8000

## Использование

### Основные страницы

- `/` - Главная страница сайта
- `/admin/leads` - Просмотр всех заявок (JSON)
- `/health` - Проверка состояния сервера

### API эндпоинты

- `POST /submit-form` - Отправка заявки
- `GET /admin/leads` - Получение всех заявок
- `GET /health` - Проверка здоровья сервера

### Структура данных заявки

```json
{
  "id": 1,
  "name": "Имя клиента",
  "services": ["site", "telegram-bot"],
  "description": "Описание проекта",
  "budget": "300-500k",
  "contact_method": "whatsapp",
  "phone": "+7 999 123-45-67",
  "telegram": "@username",
  "phone_number": "+7 999 123-45-67",
  "call_time": "10:00-18:00",
  "email": "email@example.com",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Способы связи

Форма поддерживает 4 способа связи с клиентами:
- **WhatsApp** - требует номер телефона
- **Telegram** - требует username (@username)
- **Звонок** - требует номер и удобное время
- **Email** - требует email адрес

## Развертывание

### Локальная разработка

```bash
# Режим разработки с автоперезагрузкой
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=.

# Быстрый запуск без детального вывода
pytest -q
```

### Продакшн

1. Установите uvicorn с production зависимостями:
```bash
pip install uvicorn[standard]
```

2. Запустите с uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (опционально)

Создайте Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Файлы проекта

```
Terrasite/
├── main.py             # Точка входа FastAPI приложения
├── config.py           # Конфигурация и настройки
├── routers.py          # API маршруты
├── services.py         # Бизнес-логика (файлы, email)
├── schemas.py          # Pydantic модели для валидации
├── requirements.txt    # Python зависимости
├── index.html          # Главная страница сайта
├── styles.css          # CSS стили (темная тема)
├── script.js           # JavaScript (многошаговая форма)
├── leads.json          # База данных заявок (JSON)
├── tests/              # Директория с тестами
│   ├── test_config.py
│   ├── test_routers.py
│   ├── test_schemas.py
│   └── test_services.py
└── README.md           # Документация
```

## Особенности

- ✅ **Асинхронная архитектура** - FastAPI + aiofiles + aiosmtplib
- ✅ **Валидация данных** - Pydantic v2 с кастомными валидаторами
- ✅ **Многошаговая форма** - 4 шага с валидацией на каждом
- ✅ **Множественные способы связи** - WhatsApp, Telegram, звонок, email
- ✅ **Защита от дубликатов** - проверка повторных заявок (5 минут)
- ✅ **Современный UI** - темная тема с анимациями и эффектами
- ✅ **Полное тестирование** - 39+ тестов с моками AsyncMock
- ✅ **Типизация** - строгая типизация Python с type hints

## Лицензия

MIT License

## Контакты

- Email: team.terrasite@yandex.ru
- Сайт: https://terrasite.ru (в разработке)
