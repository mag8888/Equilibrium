#!/bin/bash

echo "🚀 Starting TRINARY MLM System..."

# Проверка переменных окружения
echo "🔍 Checking environment variables..."
echo "DATABASE_HOST: $DATABASE_HOST"
echo "DATABASE_NAME: $DATABASE_NAME"
echo "DATABASE_USER: $DATABASE_USER"
echo "DATABASE_PORT: $DATABASE_PORT"

# Очистка Python кэша
echo "🧹 Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Создание директории для статических файлов
echo "📁 Creating staticfiles directory..."
mkdir -p staticfiles

# Сбор статических файлов
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Проверка подключения к базе данных
echo "🔌 Testing database connection..."
python manage.py check --database default || {
    echo "❌ Database connection failed!"
    echo "🔍 Trying to connect with psql..."
    PGPASSWORD="$DATABASE_PASSWORD" psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "SELECT 1;" || {
        echo "❌ Direct psql connection also failed!"
        echo "🔍 Checking if PostgreSQL service is running..."
        echo "🔍 Variables: HOST=$DATABASE_HOST, PORT=$DATABASE_PORT, USER=$DATABASE_USER, DB=$DATABASE_NAME"
    }
}

# Применение миграций
echo "🗄️ Applying migrations..."
python manage.py migrate

# Инициализация базы данных
echo "🔧 Initializing database..."
python manage.py auto_init

# Запуск Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn mlm_system.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
