from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import json
from typing import Optional, Dict, List
from dotenv import load_dotenv
import os
import re

from urllib.parse import urlparse, parse_qs

def safe_print(text):
    """Безопасная печать для избежания проблем с кодировкой"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Заменяем проблемные символы на безопасные
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

# Импортируем наши новые модули
from sentiment_analyzer import SentimentAnalyzer
from keyword_extractor import KeywordExtractor
from youtube_service import YouTubeService
from gemini_service import GeminiService

app = FastAPI(title="YouTube Comment Analyzer API")

# Создаем отдельный роутер для API
api_router = APIRouter(prefix="/api")

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене разрешаем все домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статические файлы (фронтенд)
# Проверяем разные возможные пути к собранному фронтенду
if os.path.exists("../frontend/dist"):
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="frontend")
    safe_print("Frontend mounted from ../frontend/dist")
elif os.path.exists("../frontend/build"):
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="frontend")
    safe_print("Frontend mounted from ../frontend/build")
elif os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
    safe_print("Frontend mounted from ../frontend")
elif os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
    safe_print("Frontend mounted from static")
else:
    safe_print("No frontend directory found")

# Загружаем переменные окружения
# Сначала пробуем .env.local (для разработки), потом .env (для продакшена)
if os.path.exists('.env.local'):
    try:
        load_dotenv('.env.local')
        safe_print("Loaded environment from .env.local (development)")
    except UnicodeDecodeError:
        safe_print("Warning: .env.local file has encoding issues, using system environment variables")
elif os.path.exists('.env'):
    try:
        load_dotenv('.env')
        safe_print("Loaded environment from .env (production)")
    except UnicodeDecodeError:
        safe_print("Warning: .env file has encoding issues, using system environment variables")
else:
    safe_print("No .env file found, using system environment variables")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "")

# Безопасное логирование (не показываем полные ключи)
safe_print(f"YOUTUBE_API_KEY loaded: {'✅ Yes' if YOUTUBE_API_KEY else '❌ No'}")
safe_print(f"GEMINI_API_KEY loaded: {'✅ Yes' if GEMINI_API_KEY else '❌ No'}")
safe_print(f"GEMINI_API_KEYS count: {len(GEMINI_API_KEYS.split(',')) if GEMINI_API_KEYS else 0}")
safe_print(f"Current working directory: {os.getcwd()}")
safe_print(f"Environment: {'🚀 Production' if os.environ.get('PORT') else '🔧 Development'}")

# Инициализируем сервисы
sentiment_analyzer = SentimentAnalyzer()
keyword_extractor = KeywordExtractor()
youtube_service = YouTubeService(YOUTUBE_API_KEY)
gemini_service = GeminiService(GEMINI_API_KEY)  # Класс сам прочитает GEMINI_API_KEYS

# Выводим статус после инициализации
safe_print(f"YouTube API available: {youtube_service.youtube is not None}")
safe_print(f"Gemini API available: {gemini_service.model is not None}")
if gemini_service.model:
    safe_print(f"Gemini model: {gemini_service.model_name}")

def extract_video_id(url: str) -> str:
    """Извлекает video_id из различных форматов YouTube URL"""
    return youtube_service.extract_video_id(url)

def validate_video_id(video_id: str) -> bool:
    """Проверяет корректность video_id"""
    return youtube_service.validate_video_id(video_id)

def calculate_engagement_rate(video_info: Dict) -> float:
    """Вычисляет engagement rate"""
    if video_info['view_count'] > 0:
        total_engagement = video_info['like_count'] + video_info['comment_count']
        return round((total_engagement / video_info['view_count']) * 100, 2)
    return 0.0

def get_popular_comments(comments: List[Dict], top_k: int = 5) -> List[Dict]:
    """Возвращает самые популярные комментарии"""
    if not comments:
        return []
    
    # Фильтруем комментарии с лайками > 0 и сортируем по лайкам
    liked_comments = [c for c in comments if c.get('likes', 0) > 0]
    
    if not liked_comments:
        # Если нет лайкнутых комментариев, берем первые 5 по релевантности
        sorted_comments = comments[:top_k]
    else:
        # Сортируем по лайкам (убывание)
        sorted_comments = sorted(liked_comments, key=lambda x: x.get('likes', 0), reverse=True)
    
    popular = []
    for comment in sorted_comments[:top_k]:
        popular.append({
            'author': comment.get('author', 'Unknown'),
            'text': comment.get('text', ''),
            'likes': comment.get('likes', 0),
            'author_avatar': comment.get('author_avatar', '')
        })
    
    return popular

@app.get("/analyze")
async def analyze_comments(video_id: str):
    """
    Анализирует комментарии к YouTube видео с реальным NLP анализом
    """
    try:
        if not video_id:
            raise HTTPException(status_code=400, detail="Video ID is required")
        
        # Проверяем корректность video_id
        if not validate_video_id(video_id):
            raise HTTPException(status_code=400, detail="Invalid video ID format")
        
        # Получаем информацию о видео
        safe_print(f"Getting video info for: {video_id}")
        video_info = youtube_service.get_video_info(video_id)
        safe_print(f"Video info result: {video_info.get('title', 'N/A') if video_info else 'None'}")
        if video_info:
            safe_print(f"Channel avatar: {video_info.get('channel_avatar', 'None')}")
            safe_print(f"Channel URL: {video_info.get('channel_url', 'None')}")
            safe_print(f"Channel ID: {video_info.get('channel_id', 'None')}")
        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found or unavailable")
        
        # Получаем комментарии
        safe_print(f"Getting comments for: {video_id}")
        comments = youtube_service.get_video_comments(video_id, max_results=100)
        safe_print(f"Comments count: {len(comments) if comments else 0}")
        if not comments:
            raise HTTPException(status_code=404, detail="No comments found for this video")
        
        # Анализируем тональность комментариев
        sentiment_analysis = sentiment_analyzer.analyze_comments(comments)
        
        # Извлекаем ключевые слова
        keyword_analysis = keyword_extractor.analyze_keywords(
            comments, 
            sentiment_analysis.get('language_distribution', {})
        )
        
        # Получаем популярные комментарии
        popular_comments = get_popular_comments(comments, 5)
        
        # Вычисляем engagement rate
        engagement_rate = calculate_engagement_rate(video_info)
        
        # Дополнительная статистика
        avg_comment_length = sum(len(c.get('text', '')) for c in comments) / len(comments) if comments else 0
        total_likes_on_comments = sum(c.get('likes', 0) for c in comments)
        
        return {
            "success": True,
            "video_info": {
                "title": video_info['title'],
                "channel": video_info.get('channel_title', 'Unknown'),
                "channel_title": video_info.get('channel_title', 'Unknown'),
                "channel_avatar": video_info.get('channel_avatar') or f"https://ui-avatars.com/api/?name={video_info.get('channel_title', 'Channel').replace(' ', '+')}&size=240&background=ff0000&color=ffffff&bold=true",
                "channel_url": video_info.get('channel_url', f"https://www.youtube.com/channel/{video_info.get('channel_id', '')}"),
                "views": video_info['view_count'],
                "likes": video_info['like_count'],
                "comments": video_info['comment_count'],
                "engagement_rate": engagement_rate,
                "published_at": video_info.get('published_at', ''),
                "duration": video_info.get('duration', ''),
                "tags": video_info.get('tags', [])
            },
            "sentiment_analysis": sentiment_analysis['sentiment_analysis'],
            "language_distribution": sentiment_analysis.get('language_distribution', {}),
            "average_sentiment": sentiment_analysis.get('average_sentiment', 0.0),
            "keywords": keyword_analysis['keywords'],
            "phrases": keyword_analysis['phrases'],
            "popular_comments": popular_comments,
            "statistics": {
                "total_comments_analyzed": sentiment_analysis.get('total_analyzed', 0),
                "average_comment_length": round(avg_comment_length, 1),
                "total_likes_on_comments": total_likes_on_comments,
                "main_language": keyword_analysis.get('main_language', 'en'),
                "total_words_analyzed": keyword_analysis.get('total_words_analyzed', 0)
            },
            # Для обратной совместимости с фронтендом
            "themes": {
                "frequently_asked_questions": len([k for k in keyword_analysis['keywords'] if 'how' in k['word'].lower() or 'что' in k['word'].lower()]),
                "high_priority_pain_points": len([c for c in comments if any(word in c.get('text', '').lower() for word in ['problem', 'issue', 'error', 'проблема', 'ошибка'])]),
                "content_requests": len([c for c in comments if any(word in c.get('text', '').lower() for word in ['please', 'can you', 'пожалуйста', 'можете'])]),
                "topics_of_interest": min(len(keyword_analysis['keywords']), 10)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        safe_print(f"Error in analyze_comments: {e}")
        safe_print(f"Error type: {type(e)}")
        import traceback
        safe_print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error analyzing comments: {str(e)}")

@app.post("/analyze-url")
async def analyze_by_url(data: dict):
    """
    Анализирует комментарии по полному URL YouTube видео
    """
    try:
        url = data.get('url', '')
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Извлекаем video_id из URL
        video_id = extract_video_id(url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Используем существующую функцию анализа
        return await analyze_comments(video_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")

@app.get("/keywords/{video_id}")
async def get_keywords_only(video_id: str):
    """
    Возвращает только ключевые слова для видео (быстрый анализ)
    """
    try:
        if not validate_video_id(video_id):
            raise HTTPException(status_code=400, detail="Invalid video ID format")
        
        # Получаем комментарии
        comments = youtube_service.get_video_comments(video_id, max_results=50)
        if not comments:
            raise HTTPException(status_code=404, detail="No comments found")
        
        # Быстрый анализ языка
        languages = {}
        for comment in comments[:10]:  # Анализируем первые 10 комментариев для определения языка
            lang = sentiment_analyzer.detect_language(comment.get('text', ''))
            languages[lang] = languages.get(lang, 0) + 1
        
        # Извлекаем ключевые слова
        keyword_analysis = keyword_extractor.analyze_keywords(comments, languages)
        
        return {
            "success": True,
            "keywords": keyword_analysis['keywords'],
            "phrases": keyword_analysis['phrases'],
            "main_language": keyword_analysis.get('main_language', 'en')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting keywords: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "YouTube Comment Analyzer API - Enhanced",
        "youtube_api": youtube_service.youtube is not None,
        "gemini_api": gemini_service.model is not None,
        "port": os.environ.get("PORT", "8001"),
        "features": [
            "Real NLP sentiment analysis",
            "Keyword extraction with TF-IDF",
            "Multi-language support (EN/RU)",
            "YouTube API integration",
            "Advanced statistics",
            "Clever AI video analysis"
        ]
    }

@app.get("/ping")
async def ping():
    import time
    return {"message": "pong", "timestamp": time.time()}

@app.get("/test-avatar/{video_id}")
async def test_avatar(video_id: str):
    """Тестирует получение аватара канала"""
    try:
        if not validate_video_id(video_id):
            raise HTTPException(status_code=400, detail="Invalid video ID format")
        
        video_info = youtube_service.get_video_info(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "success": True,
            "video_id": video_id,
            "channel_title": video_info.get('channel_title'),
            "channel_id": video_info.get('channel_id'),
            "channel_avatar": video_info.get('channel_avatar'),
            "channel_url": video_info.get('channel_url'),
            "fallback_avatar": f"https://ui-avatars.com/api/?name={video_info.get('channel_title', 'Channel').replace(' ', '+')}&size=240&background=ff0000&color=ffffff&bold=true"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/test-gemini")
async def test_gemini():
    """Тестирует подключение к Gemini API"""
    result = gemini_service.test_connection()
    if result['success']:
        return result
    else:
        raise HTTPException(status_code=500, detail=result['message'])

@app.get("/gemini-status")
async def gemini_status():
    """Проверяет статус и квоты Gemini API"""
    try:
        # Простой тест с минимальным запросом
        test_result = gemini_service.test_connection()
        
        return {
            "api_key_configured": gemini_service.api_key is not None,
            "model_initialized": gemini_service.model is not None,
            "current_model": gemini_service.model_name,
            "test_connection": test_result,
            "recommendations": [
                "Используйте gemini-1.5-flash для экономии квоты",
                "Лимит: 15 запросов в минуту, 1500 в день",
                "При превышении ждите 1-2 минуты"
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "api_key_configured": gemini_service.api_key is not None,
            "model_initialized": False
        }

@app.post("/gemini-analysis")
async def gemini_analysis(data: dict):
    """
    Анализирует видео и комментарии через Gemini AI
    """
    try:
        video_id = data.get('video_id', '')
        if not video_id:
            raise HTTPException(status_code=400, detail="Video ID is required")
        
        # Проверяем корректность video_id
        if not validate_video_id(video_id):
            raise HTTPException(status_code=400, detail="Invalid video ID format")
        
        # Получаем информацию о видео
        video_info = youtube_service.get_video_info(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found or unavailable")
        
        # Получаем ВСЕ доступные комментарии (увеличиваем лимит)
        comments = youtube_service.get_video_comments(video_id, max_results=200)
        if not comments:
            raise HTTPException(status_code=404, detail="No comments found for this video")
        
        # Формируем URL видео
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Отправляем на анализ в Gemini
        analysis_result = gemini_service.analyze_video_with_comments(
            video_url, video_info, comments
        )
        
        if not analysis_result.get('success'):
            raise HTTPException(
                status_code=500, 
                detail=analysis_result.get('error', 'Unknown error occurred')
            )
        
        return {
            "success": True,
            "video_info": {
                "title": video_info['title'],
                "channel": video_info.get('channel_title', 'Unknown'),
                "channel_avatar": video_info.get('channel_avatar') or f"https://ui-avatars.com/api/?name={video_info.get('channel_title', 'Channel').replace(' ', '+')}&size=240&background=ff0000&color=ffffff&bold=true",
                "channel_url": video_info.get('channel_url', f"https://www.youtube.com/channel/{video_info.get('channel_id', '')}"),
                "views": video_info['view_count'],
                "likes": video_info['like_count'],
                "comments_analyzed": len(comments)
            },
            "gemini_analysis": analysis_result['analysis'],
            "timestamp": analysis_result['timestamp']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        safe_print(f"Error in gemini_analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error during Gemini analysis: {str(e)}")

# Обслуживаем статические файлы фронтенда
@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    """Обслуживает статические ресурсы фронтенда"""
    frontend_paths = ["../frontend/dist", "../frontend/build", "../frontend", "static", "frontend"]
    
    for frontend_dir in frontend_paths:
        asset_path = f"{frontend_dir}/assets/{file_path}"
        if os.path.exists(asset_path) and os.path.isfile(asset_path):
            return FileResponse(asset_path)
    
    raise HTTPException(status_code=404, detail="Asset not found")

# Тестовый API endpoint (работал раньше)
@app.get("/test-api")
async def test_api():
    return {
        "message": "YouTube Comment Analyzer API - Enhanced with Real NLP",
        "youtube_api_available": youtube_service.youtube is not None,
        "gemini_api_available": gemini_service.model is not None,
        "gemini_model": gemini_service.model_name if gemini_service.model else None,
        "status": "API is working!"
    }

# Главная страница фронтенда
@app.get("/")
async def serve_index():
    """Обслуживает главную страницу фронтенда"""
    frontend_paths = ["../frontend/dist", "../frontend/build", "../frontend", "static", "frontend"]
    
    for frontend_dir in frontend_paths:
        index_path = f"{frontend_dir}/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # Fallback на API информацию если фронтенд не найден
    return {
        "message": "YouTube Comment Analyzer API - Enhanced with Real NLP",
        "youtube_api_available": youtube_service.youtube is not None,
        "gemini_api_available": gemini_service.model is not None,
        "gemini_model": gemini_service.model_name if gemini_service.model else None
    }

# Специфичные SPA роуты (добавляйте по мере необходимости)
@app.get("/dashboard")
@app.get("/settings") 
@app.get("/about")
async def serve_spa_routes():
    """Обслуживает известные SPA роуты"""
    frontend_paths = ["../frontend/dist", "../frontend/build", "../frontend", "static", "frontend"]
    
    for frontend_dir in frontend_paths:
        index_path = f"{frontend_dir}/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Frontend not found")

if __name__ == "__main__":
    import uvicorn
    
    # Выводим информацию о зарегистрированных роутах
    safe_print("🔧 Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            safe_print(f"  {route.methods} {route.path}")
    
    # Render автоматически устанавливает PORT, локально используем 8000
    port = int(os.environ.get("PORT", 8000))
    safe_print(f"🚀 Starting YouTube Comment Analyzer on port {port}")
    safe_print(f"🌐 Environment: {'Production' if os.environ.get('PORT') else 'Development'}")
    safe_print(f"🔗 Binding to host: 0.0.0.0:{port}")
    
    # Запускаем с правильными параметрами для Render
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )
