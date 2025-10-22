# Railway Deployment Guide

## Настройка для Railway

### 1. Подключение к GitHub
1. Перейдите на [Railway](https://railway.app)
2. Войдите в аккаунт и нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Подключите репозиторий `https://github.com/mag8888/Equilibrium`

### 2. Настройка переменных окружения
В Railway Dashboard добавьте следующие переменные:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
MONGO_URL=mongodb://localhost:27017/
MONGO_DB_NAME=mlm_system
MONGO_USERNAME=
MONGO_PASSWORD=
MONGO_AUTH_SOURCE=admin
```

### 3. Добавление MongoDB
1. В Railway Dashboard нажмите "New Service"
2. Выберите "Database" → "MongoDB"
3. Railway автоматически создаст MongoDB и добавит переменные окружения

### 4. Настройка домена
1. В настройках сервиса перейдите в "Settings"
2. В разделе "Domains" добавьте кастомный домен (опционально)
3. Railway автоматически предоставит домен вида `your-app.railway.app`

## Локальная разработка

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка переменных окружения
Создайте файл `.env`:
```
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Запуск локально
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Структура проекта

```
mlm_system/
├── users/                 # Модуль пользователей
├── admin_panel/          # Кастомная админ панель
├── payments/             # Модуль платежей
├── mlm_system/          # Основные настройки Django
├── requirements.txt     # Зависимости Python
├── Procfile            # Конфигурация для Railway
├── railway.json        # Дополнительные настройки Railway
└── railway.toml        # Переменные окружения Railway
```

## Мониторинг

Railway предоставляет:
- Логи в реальном времени
- Метрики производительности
- Мониторинг базы данных
- Автоматические деплои при push в GitHub

## Безопасность

- Все секретные ключи хранятся в переменных окружения Railway
- HTTPS включен по умолчанию
- CORS настроен для production
- WhiteNoise для статических файлов
