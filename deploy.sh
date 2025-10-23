#!/bin/bash

echo "🚀 Деплой TRINARY MLM на Railway..."

# Применение миграций
echo "📦 Применение миграций..."
python manage.py migrate

# Инициализация базы данных
echo "🔧 Инициализация базы данных..."
python manage.py init_railway

# Сбор статических файлов
echo "📁 Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "✅ Деплой завершен!"
echo "🌐 Приложение доступно по адресу: https://web-production-48c0.up.railway.app/"
echo "👤 Админ-доступ: admin / admin123"
