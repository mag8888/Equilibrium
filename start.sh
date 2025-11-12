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
# В Docker образе мы всегда используем backend/
if [ -f "manage.py" ]; then
    echo "📁 Using backend/ structure (current directory)..."
    WSGI_MODULE="equilibrium_backend.wsgi:application"
elif [ -f "../backend/manage.py" ]; then
    echo "📁 Detected backend/ structure, switching to backend directory..."
    cd ../backend
    WSGI_MODULE="equilibrium_backend.wsgi:application"
else
    echo "❌ No manage.py found in backend/!"
    echo "🔍 Current directory: $(pwd)"
    echo "🔍 Files: $(ls -la)"
    exit 1
fi

# Минимальная подготовка - только самое необходимое
echo "📦 Quick setup (minimal)..."
timeout 10 python manage.py collectstatic --noinput 2>&1 | head -5 || echo "⚠️ Collectstatic skipped"

# Применение миграций (быстрое, не блокирующее)
echo "🗄️ Applying migrations (quick)..."
timeout 15 python manage.py migrate --noinput 2>&1 | head -10 || {
    echo "⚠️ Migrations timed out, but continuing..."
}

# Запуск простого healthcheck сервера в фоне (не требует Django)
echo "🏥 Starting simple healthcheck server..."
HEALTHCHECK_PORT=${HEALTHCHECK_PORT:-8001}
python3 ../simple_healthcheck.py &
HEALTHCHECK_PID=$!
echo "✅ Healthcheck server started on port $HEALTHCHECK_PORT (PID: $HEALTHCHECK_PID)"

# Запуск Gunicorn СРАЗУ (основной процесс через exec для healthcheck)
echo "🌐 Starting Gunicorn server NOW..."
PORT=${PORT:-8000}
echo "🚀 Server will be available on port $PORT"
echo "✅ Healthcheck endpoint: /health/ (also on port $HEALTHCHECK_PORT)"
echo "⏳ Gunicorn starting as main process (exec)..."
echo "📝 Current directory: $(pwd)"
echo "📝 Python path: $PYTHONPATH"
echo "📝 WSGI module: $WSGI_MODULE"

# Проверяем что Django может импортироваться
echo "🔍 Testing Django import..."
python -c "import django; print(f'Django version: {django.get_version()}')" || {
    echo "❌ Django import failed!"
    exit 1
}

# Используем exec чтобы Gunicorn стал основным процессом контейнера
# Минимальные настройки для максимально быстрого старта
# Добавляем info логи для диагностики
echo "✅ Starting Gunicorn..."
exec gunicorn $WSGI_MODULE \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    --graceful-timeout 30 \
    --capture-output \
    --enable-stdio-inheritance
