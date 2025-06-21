# 🎬 YouTube Comment Analyzer

Продвинутый анализатор комментариев YouTube с использованием NLP и AI.

## ✨ Возможности

- **📊 NLP анализ тональности** - реальный анализ эмоций комментариев
- **🔍 Извлечение ключевых слов** - TF-IDF алгоритм для поиска важных тем
- **🌍 Многоязычность** - поддержка русского и английского языков
- **🤖 AI анализ** - глубокий анализ через Gemini AI
- **📈 Статистика** - детальная аналитика видео и комментариев
- **🎯 Прямые ссылки** - корректные ссылки на каналы (@username формат)

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка API ключей
Скопируйте `.env.example` в `.env` и добавьте ваши ключи:
```bash
cp .env.example .env
```

Заполните файл `.env`:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_KEYS=key1,key2,key3  # Несколько ключей для ротации
```

### 3. Запуск сервера
```bash
python main.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

## 📡 API Endpoints

### Основные endpoints:
- `GET /` - информация о сервисе
- `GET /analyze?video_id={id}` - анализ комментариев
- `POST /analyze-url` - анализ по URL видео
- `POST /gemini-analysis` - AI анализ через Gemini
- `GET /health` - проверка состояния сервиса

### Утилиты:
- `GET /ping` - проверка доступности
- `GET /test-gemini` - тест Gemini API
- `GET /gemini-status` - статус и квоты Gemini

## 🔧 Структура проекта

```
backend/
├── main.py              # Основной FastAPI сервер
├── youtube_service.py   # Сервис YouTube API
├── gemini_service.py    # Сервис Gemini AI
├── sentiment_analyzer.py # Анализ тональности
├── keyword_extractor.py # Извлечение ключевых слов
├── test_apis.py         # Тест API ключей
├── requirements.txt     # Зависимости Python
├── .env.example        # Пример конфигурации
└── README.md           # Документация
```

## 🎯 Примеры использования

### Анализ видео по ID:
```bash
curl "http://localhost:8000/analyze?video_id=dQw4w9WgXcQ"
```

### Анализ видео по URL:
```bash
curl -X POST "http://localhost:8000/analyze-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### AI анализ через Gemini:
```bash
curl -X POST "http://localhost:8000/gemini-analysis" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "dQw4w9WgXcQ"}'
```

## 📊 Пример ответа API

```json
{
  "success": true,
  "video_info": {
    "title": "Video Title",
    "channel_title": "Channel Name",
    "channel_avatar": "https://...",
    "channel_url": "https://www.youtube.com/@username",
    "views": 1000000,
    "likes": 50000,
    "comments": 1500,
    "engagement_rate": 5.15
  },
  "sentiment_analysis": {
    "excited": 45,
    "neutral": 35,
    "confused": 15,
    "frustrated": 5
  },
  "keywords": [
    {"word": "amazing", "frequency": 25, "relevance": 0.85},
    {"word": "tutorial", "frequency": 18, "relevance": 0.72}
  ],
  "popular_comments": [...]
}
```

## 🔑 Получение API ключей

### YouTube Data API v3:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите YouTube Data API v3
4. Создайте API ключ в разделе "Credentials"

### Gemini API:
1. Перейдите в [Google AI Studio](https://aistudio.google.com/)
2. Создайте новый API ключ
3. Для лучшей производительности создайте несколько ключей

## 🛠️ Разработка

### Тестирование API ключей:
```bash
python test_apis.py
```

### Проверка состояния сервисов:
```bash
curl "http://localhost:8000/health"
```

## 📝 Лицензия

MIT License - используйте свободно для любых целей.

## 🤝 Поддержка

Если у вас есть вопросы или предложения, создайте issue в репозитории.

---

**Проект готов к продакшену!** 🚀
