# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы
COPY . .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r backend/requirements.txt

# Собираем фронтенд
WORKDIR /app/frontend
RUN npm ci --only=production
RUN npm run build

# Возвращаемся в корень и копируем статику
WORKDIR /app
RUN mkdir -p backend/static
RUN cp -r frontend/dist/* backend/static/

# Переходим в backend
WORKDIR /app/backend

# Открываем порт
EXPOSE 10000

# Запускаем приложение
CMD ["python", "main.py"]
