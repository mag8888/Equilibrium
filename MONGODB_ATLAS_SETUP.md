# 🗄️ MongoDB Atlas Setup Guide

## Настройка MongoDB Atlas для MLM System

### 1. Получение строки подключения

У вас уже есть строка подключения:
```
mongodb+srv://<db_username>:<db_password>@equilibrium.0ugezsh.mongodb.net/?retryWrites=true&w=majority&appName=Equilibrium
```

### 2. Извлечение данных из строки подключения

Из вашей строки подключения нужно извлечь:
- **Username**: `<db_username>`
- **Password**: `<db_password>`
- **Database**: `mlm_system` (будет создана автоматически)

### 3. Настройка переменных окружения

#### Для локальной разработки:
Создайте файл `.env` в корне проекта:
```bash
# MongoDB Atlas Configuration
MONGO_URL=mongodb+srv://<db_username>:<db_password>@equilibrium.0ugezsh.mongodb.net/?retryWrites=true&w=majority&appName=Equilibrium
MONGO_DB_NAME=mlm_system
MONGO_USERNAME=<db_username>
MONGO_PASSWORD=<db_password>
MONGO_AUTH_SOURCE=admin

# Django Settings
SECRET_KEY=django-insecure-change-me-in-production-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Для Railway:
В Railway Dashboard → Settings → Variables добавьте:
```bash
MONGO_URL=mongodb+srv://<db_username>:<db_password>@equilibrium.0ugezsh.mongodb.net/?retryWrites=true&w=majority&appName=Equilibrium
MONGO_DB_NAME=mlm_system
MONGO_USERNAME=<db_username>
MONGO_PASSWORD=<db_password>
MONGO_AUTH_SOURCE=admin
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
```

### 4. Настройка IP Whitelist в MongoDB Atlas

1. **Перейдите в MongoDB Atlas Dashboard**
2. **Network Access** → **Add IP Address**
3. **Добавьте IP адреса:**
   - `0.0.0.0/0` (для Railway - все IP)
   - Ваш локальный IP для разработки

### 5. Настройка пользователя базы данных

1. **Database Access** → **Add New Database User**
2. **Username**: `<db_username>`
3. **Password**: `<db_password>`
4. **Database User Privileges**: `Read and write to any database`

### 6. Запуск миграций

После настройки переменных окружения:

```bash
# Локально
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# На Railway (через Railway CLI или Dashboard)
railway run python manage.py makemigrations
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

### 7. Проверка подключения

```python
# В Django shell
python manage.py shell

# Проверка подключения
from django.db import connection
connection.ensure_connection()
print("MongoDB подключение успешно!")
```

### 8. Структура базы данных

MongoDB Atlas автоматически создаст коллекции:
- `users_user` - пользователи
- `users_bonus` - бонусы
- `users_partnerstructure` - структура партнеров
- `payments_payment` - платежи

### 9. Мониторинг

MongoDB Atlas предоставляет:
- 📊 **Метрики производительности**
- 📝 **Логи запросов**
- 🔒 **Мониторинг безопасности**
- 💾 **Backup и восстановление**

### 10. Безопасность

- ✅ **SSL/TLS** включен по умолчанию
- ✅ **Аутентификация** через username/password
- ✅ **IP Whitelist** для доступа
- ✅ **Шифрование** данных в покое и в движении

## 🚀 Готово!

После настройки MongoDB Atlas ваша MLM система будет:
- ✅ Хранить данные в облачной MongoDB
- ✅ Автоматически масштабироваться
- ✅ Иметь резервные копии
- ✅ Работать с высокой производительностью

**Следующий шаг**: Настройте переменные окружения и запустите миграции!
