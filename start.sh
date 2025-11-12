#!/bin/sh
set -ex
cd /app/backend
python manage.py migrate --noinput
PORT=${PORT:-8000}
exec gunicorn equilibrium_backend.wsgi:application --bind 0.0.0.0:$PORT
