# 🚀 TRINARY MLM - Деплой на Railway

## ✅ Код загружен на GitHub!
**Репозиторий**: https://github.com/mag8888/Equilibrium.git

## 🎯 Следующие шаги для деплоя на Railway:

### 1. Создайте проект на Railway
1. Зайдите на [Railway.app](https://railway.app)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Подключите репозиторий: `https://github.com/mag8888/Equilibrium.git`

### 2. Добавьте PostgreSQL базу данных
1. В панели Railway нажмите "+ New"
2. Выберите "Database" → "PostgreSQL"
3. Railway автоматически создаст базу данных

### 3. Установите переменные окружения
В настройках проекта добавьте:

```
DEBUG=False
SECRET_KEY=your-very-secret-key-here-make-it-long-and-random-123456789
DATABASE_NAME=railway
DATABASE_USER=postgres
DATABASE_PASSWORD=your-database-password-from-railway
DATABASE_HOST=your-database-host.railway.app
DATABASE_PORT=5432
```

### 4. После деплоя выполните инициализацию
В Railway Console выполните:

```bash
python manage.py migrate
python manage.py init_railway
python manage.py collectstatic --noinput
```

## 🌐 После деплоя будет доступно:

- **Главная**: `https://web-production-48c0.up.railway.app/`
- **Регистрация**: `https://web-production-48c0.up.railway.app/register/`
- **Админ-панель**: `https://web-production-48c0.up.railway.app/admin-panel/`
- **Django Admin**: `https://web-production-48c0.up.railway.app/admin/`

## 👤 Доступы:
- **Логин**: admin
- **Пароль**: admin123

## 🎉 Система готова!

**TRINARY MLM** - полная микро-модульная система с:
- ✅ Регистрацией по реферальным ссылкам
- ✅ MLM структурой с автоматическим размещением
- ✅ Зелеными и красными бонусами
- ✅ Админ-панелью с визуализацией
- ✅ Системой платежей и выводов
- ✅ Настройками для Railway

**Код загружен и готов к деплою!** 🚀
