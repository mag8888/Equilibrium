# 🚀 Railway Deployment Setup

## Шаги для деплоя на Railway

### 1. Подготовка репозитория
✅ Код уже загружен на GitHub: https://github.com/mag8888/Equilibrium

### 2. Создание проекта на Railway

1. **Перейдите на [Railway.app](https://railway.app)**
2. **Войдите в аккаунт** (через GitHub)
3. **Нажмите "New Project"**
4. **Выберите "Deploy from GitHub repo"**
5. **Найдите и выберите репозиторий `mag8888/Equilibrium`**

### 3. Настройка переменных окружения

В Railway Dashboard → Settings → Variables добавьте:

```bash
SECRET_KEY=django-insecure-railway-production-key-12345
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
```

### 4. Добавление MongoDB

1. **В Railway Dashboard нажмите "New Service"**
2. **Выберите "Database" → "MongoDB"**
3. **Railway автоматически добавит переменные:**
   - `MONGO_URL`
   - `MONGO_DB_NAME`
   - `MONGO_USERNAME`
   - `MONGO_PASSWORD`
   - `MONGO_AUTH_SOURCE`

### 5. Настройка деплоя

Railway автоматически:
- ✅ Обнаружит `requirements.txt`
- ✅ Использует `Procfile` для запуска
- ✅ Применит настройки из `railway.json`
- ✅ Настроит переменные из `railway.toml`

### 6. Первый запуск

После деплоя выполните миграции:

```bash
# В Railway Dashboard → Deployments → View Logs
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Доступ к приложению

- **Админ панель**: `https://your-app.railway.app/admin-panel/`
- **Django Admin**: `https://your-app.railway.app/admin/`
- **API**: `https://your-app.railway.app/api/`

## 🔧 Конфигурация файлов

### Procfile
```
web: gunicorn mlm_system.wsgi:application --bind 0.0.0.0:$PORT
```

### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn mlm_system.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/admin-panel/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### railway.toml
```toml
[env]
SECRET_KEY = "django-insecure-change-me-in-production-railway-12345"
DEBUG = "False"
ALLOWED_HOSTS = "*.railway.app,*.up.railway.app"
```

## 📊 Мониторинг

Railway предоставляет:
- 📈 **Метрики производительности**
- 📝 **Логи в реальном времени**
- 🔄 **Автоматические деплои**
- 💾 **Мониторинг базы данных**
- 🔒 **HTTPS по умолчанию**

## 🛠️ Локальная разработка

```bash
# Клонирование репозитория
git clone https://github.com/mag8888/Equilibrium.git
cd Equilibrium

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env

# Запуск миграций
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver
```

## 🔐 Безопасность

- ✅ Все секреты в переменных окружения
- ✅ HTTPS включен автоматически
- ✅ CORS настроен для production
- ✅ WhiteNoise для статических файлов
- ✅ Debug отключен в production

## 📱 API Endpoints

- `GET /api/users/` - Список пользователей
- `POST /api/users/register/` - Регистрация
- `GET /api/users/{id}/structure/` - Структура пользователя
- `POST /api/users/{id}/process_payment/` - Обработка платежа
- `GET /api/payments/` - Список платежей

## 🎯 Функции системы

- 👥 **Управление пользователями**
- 💰 **Система платежей**
- 🎁 **Автоматические бонусы**
- 📊 **Админ панель**
- 🔄 **MLM логика**
- 📈 **Статистика**

---

**Готово!** 🎉 Система готова к деплою на Railway с MongoDB!
