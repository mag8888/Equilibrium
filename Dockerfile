FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект (и корневую структуру, и backend если есть)
COPY . .

# Копируем start.sh в корень
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Устанавливаем рабочую директорию в зависимости от структуры
# Если есть backend/manage.py, используем backend, иначе корень
WORKDIR /app

CMD ["./start.sh"]
