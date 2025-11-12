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

# Определяем структуру проекта
if [ -f "backend/manage.py" ]; then
    echo "📁 Detected backend/ structure, switching to backend directory..."
    cd backend
    WSGI_MODULE="equilibrium_backend.wsgi:application"
elif [ -f "manage.py" ]; then
    echo "📁 Using root structure..."
    WSGI_MODULE="mlm_system.wsgi:application"
else
    echo "❌ No manage.py found!"
    exit 1
fi

# Сбор статических файлов
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "⚠️ Collectstatic failed, but continuing..."
}

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
python manage.py migrate || {
    echo "⚠️ Migrations failed, but continuing..."
}

# Запуск Gunicorn (основной процесс должен быть первым для healthcheck)
echo "🌐 Starting Gunicorn server..."
PORT=${PORT:-8000}
echo "🚀 Server will be available on port $PORT"
echo "✅ Healthcheck endpoint: /health/"

# Запускаем Gunicorn в фоне для быстрого ответа на healthcheck
gunicorn $WSGI_MODULE --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - &
GUNICORN_PID=$!

# Даем серверу время на запуск перед healthcheck
sleep 2
echo "✅ Gunicorn started, healthcheck should work now"

# Инициализация базы данных (в фоне, не блокирует healthcheck)
echo "🔧 Initializing database (background)..."
(python manage.py auto_init && python manage.py create_superuser) 2>&1 | head -30 || {
    echo "⚠️ Initialization completed with warnings"
} &

# Ждем Gunicorn (основной процесс)
wait $GUNICORN_PID
