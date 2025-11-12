FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем requirements.txt из backend (приоритет) или корня
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r ../requirements.txt

# Копируем ТОЛЬКО backend директорию (новый проект)
COPY backend/ ./backend/

# Копируем start.sh и simple_healthcheck.py
COPY start.sh ./start.sh
COPY backend/simple_healthcheck.py ./simple_healthcheck.py
RUN chmod +x ./start.sh ./simple_healthcheck.py

# Устанавливаем рабочую директорию в backend
WORKDIR /app/backend

CMD ["../start.sh"]
