#!/bin/bash

# 🚀 Скрипт запуска для продакшена

echo "🔧 Starting YouTube Comment Analyzer..."
echo "📍 Environment: Production"
echo "🌐 Port: ${PORT:-8000}"

# Проверяем наличие необходимых переменных окружения
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "❌ ERROR: YOUTUBE_API_KEY not set"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ ERROR: GEMINI_API_KEY not set"
    exit 1
fi

echo "✅ Environment variables validated"
echo "🚀 Starting server..."

# Запускаем приложение
python main.py
