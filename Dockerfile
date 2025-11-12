FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем requirements.txt из backend (приоритет) или корня
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r ../requirements.txt

# Копируем ТОЛЬКО backend директорию (новый проект)
COPY backend/ ./backend/

# Копируем start.sh в корень /app
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Устанавливаем рабочую директорию в backend
WORKDIR /app/backend

# Запускаем start.sh из корня
CMD ["/app/start.sh"]
