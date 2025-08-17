# Сайт Terrasite

Cайт для команды Terrasite с формой заявок.

## Технологии

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **База данных**: JSON файл
- **Email**: SMTP через Yandex

## Установка и запуск

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Настройте email конфигурацию (опционально)

В файле `app.py` обновите настройки EMAIL_CONFIG:

```python
EMAIL_CONFIG = {
    'smtp_host': 'your-smtp-host',
    'smtp_port': 465,
    'smtp_user': 'your-email@domain.com',
    'smtp_password': 'your-app-password',
    'from_email': 'your-email@domain.com',
    'to_email': 'notifications@domain.com'
}
```

### 3. Запустите сервер

```bash
python app.py
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
  "email": "email@example.com",
  "services": ["site", "telegram-bot"],
  "description": "Описание проекта",
  "budget": "300-500k",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Развертывание

### Локальная разработка

```bash
export DEBUG=true
python app.py
```

### Продакшн

1. Установите gunicorn:
```bash
pip install gunicorn
```

2. Запустите с gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (опционально)

Создайте Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Файлы проекта

```
terrasite-website/
├── index.html          # Главная страница
├── styles.css          # Стили сайта
├── script.js           # JavaScript логика
├── app.py              # Backend на Flask
├── requirements.txt    # Python зависимости
├── leads.json          # Файл с заявками (создается автоматически)
├── app.log             # Логи приложения
└── README.md           # Документация
```

## Лицензия

MIT License

## Контакты

- Email: team.terrasite@yandex.ru
- Сайт: https://terrasite.ru (в разработке)
