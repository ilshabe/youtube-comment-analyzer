# 🚀 Руководство по деплою на Render

## 📋 Подготовка к деплою

### 1. Подготовка GitHub репозитория

1. **Создайте репозиторий на GitHub:**
   - Перейдите на https://github.com/new
   - Название: `youtube-comment-analyzer`
   - Сделайте публичным или приватным (на ваш выбор)

2. **Инициализируйте Git в проекте:**
   ```bash
   cd C:\Users\anon\Desktop\yt-comment-analyzer
   git init
   git add .
   git commit -m "Initial commit: YouTube Comment Analyzer"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/youtube-comment-analyzer.git
   git push -u origin main
   ```

### 2. Настройка Render

1. **Создайте аккаунт на Render:**
   - Перейдите на https://render.com/
   - Зарегистрируйтесь через GitHub

2. **Создайте новый Web Service:**
   - Нажмите "New +" → "Web Service"
   - Подключите ваш GitHub репозиторий
   - Выберите `youtube-comment-analyzer`

3. **Настройте параметры деплоя:**
   ```
   Name: youtube-comment-analyzer
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

4. **Добавьте переменные окружения:**
   В разделе "Environment Variables" добавьте:
   
   ```
   YOUTUBE_API_KEY = ваш_youtube_api_ключ
   GEMINI_API_KEY = ваш_основной_gemini_ключ
   GEMINI_API_KEYS = ключ1,ключ2,ключ3,ключ4,ключ5
   ```

   ⚠️ **ВАЖНО:** Используйте ваши реальные API ключи из файла `.env.local`

### 3. Получение API ключей

#### YouTube Data API v3:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите "YouTube Data API v3"
4. Создайте API ключ в разделе "Credentials"
5. Скопируйте ключ в переменную `YOUTUBE_API_KEY`

#### Gemini API:
1. Перейдите в [Google AI Studio](https://aistudio.google.com/)
2. Создайте API ключ
3. Для лучшей производительности создайте 5-10 ключей
4. Основной ключ → `GEMINI_API_KEY`
5. Все ключи через запятую → `GEMINI_API_KEYS`

### 4. Деплой

1. **Нажмите "Create Web Service"**
2. **Дождитесь завершения билда** (5-10 минут)
3. **Получите URL вашего приложения:** `https://your-app-name.onrender.com`

### 5. Проверка работы

После деплоя проверьте:

```bash
# Проверка здоровья сервиса
curl https://your-app-name.onrender.com/health

# Проверка API
curl https://your-app-name.onrender.com/

# Тест анализа (замените VIDEO_ID)
curl "https://your-app-name.onrender.com/analyze?video_id=dQw4w9WgXcQ"
```

## 🔧 Настройка фронтенда

Если у вас есть фронтенд, обновите API URL:

```javascript
// Вместо localhost используйте URL Render
const API_BASE = 'https://your-app-name.onrender.com';
```

## 🚨 Важные моменты

### Безопасность:
- ✅ API ключи НЕ попадают в GitHub
- ✅ Ключи хранятся только в переменных окружения Render
- ✅ `.env.local` добавлен в `.gitignore`

### Ограничения бесплатного тарифа Render:
- 🕐 Сервис "засыпает" после 15 минут неактивности
- ⏱️ Первый запрос после сна может занять 30-60 секунд
- 💾 750 часов в месяц (достаточно для тестирования)

### Мониторинг:
- 📊 Логи доступны в панели Render
- 🔍 Используйте `/health` для проверки статуса
- 📈 Следите за использованием API квот

## 🎯 Готово!

После выполнения всех шагов ваше приложение будет доступно по адресу:
`https://your-app-name.onrender.com`

### Полезные ссылки:
- 📚 [Документация Render](https://render.com/docs)
- 🎬 [YouTube Data API](https://developers.google.com/youtube/v3)
- 🤖 [Gemini API](https://ai.google.dev/)
