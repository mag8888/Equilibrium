# 🚀 Инструкции по деплою TRINARY MLM на Railway

## 📋 Что уже готово

✅ **Полная система TRINARY MLM** с микро-модульной архитектурой  
✅ **Админ-панель** с визуализацией структуры  
✅ **Система регистрации** по реферальным ссылкам  
✅ **MLM логика** с зелеными и красными бонусами  
✅ **Автоматическое размещение** в структуре  
✅ **Система платежей** и выводов средств  
✅ **Настройки для Railway** (PostgreSQL, WhiteNoise, Gunicorn)  

## 🎯 Следующие шаги для деплоя

### 1. Загрузите код на GitHub
```bash
git init
git add .
git commit -m "TRINARY MLM System ready for Railway"
git remote add origin https://github.com/your-username/trinary-mlm.git
git push -u origin main
```

### 2. Настройте Railway проект
1. Зайдите на [Railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Добавьте PostgreSQL сервис

### 3. Установите переменные окружения
В панели Railway добавьте:

```
DEBUG=False
SECRET_KEY=your-very-secret-key-here-make-it-long-and-random
DATABASE_NAME=railway
DATABASE_USER=postgres
DATABASE_PASSWORD=your-database-password
DATABASE_HOST=your-database-host.railway.app
DATABASE_PORT=5432
```

### 4. После деплоя выполните инициализацию
```bash
python manage.py migrate
python manage.py init_railway
python manage.py collectstatic --noinput
```

## 🌐 URL-ы после деплоя

- **Главная**: `https://web-production-48c0.up.railway.app/`
- **Регистрация**: `https://web-production-48c0.up.railway.app/register/`
- **Админ-панель**: `https://web-production-48c0.up.railway.app/admin-panel/`
- **Django Admin**: `https://web-production-48c0.up.railway.app/admin/`

## 👤 Доступы

- **Логин**: admin
- **Пароль**: admin123

## 🔧 Файлы для деплоя

- `requirements.txt` - зависимости Python
- `Procfile` - команда запуска для Railway
- `railway.json` - конфигурация Railway
- `deploy.sh` - скрипт автоматического деплоя
- `init_railway.py` - команда инициализации базы данных

## 📱 Тестирование функций

### 1. Регистрация пользователей
- Перейдите на `/register/`
- Зарегистрируйте несколько пользователей
- Проверьте размещение в структуре

### 2. Платежи и бонусы
- Оплатите $100 для получения статуса партнера
- Проверьте начисление зеленых и красных бонусов
- Убедитесь в правильном размещении в структуре

### 3. Админ-панель
- Управление пользователями
- Визуализация MLM структуры
- Обработка выводов средств
- Настройки системы

## 🎉 Готово к использованию!

Система полностью готова для деплоя на Railway. Все модули реализованы:

- ✅ **Пользователи**: регистрация, профили, ранги
- ✅ **MLM**: структура, бонусы, размещение
- ✅ **Платежи**: обработка, статусы, выводы
- ✅ **Админка**: управление, визуализация, настройки
- ✅ **UI**: современный интерфейс с Bootstrap 5

**Система будет работать на `https://web-production-48c0.up.railway.app/`**
