#!/bin/sh
set -e
cd /app/backend
python manage.py migrate --noinput
gunicorn equilibrium_backend.wsgi:application --bind 0.0.0.0:$PORT
