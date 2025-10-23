#!/bin/bash

echo "🚀 Starting TRINARY MLM System..."

# Создание директории для статических файлов
echo "📁 Creating staticfiles directory..."
mkdir -p staticfiles

# Сбор статических файлов
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Применение миграций
echo "🗄️ Applying migrations..."
python manage.py migrate

# Инициализация базы данных
echo "🔧 Initializing database..."
python manage.py auto_init

# Запуск Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn mlm_system.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
