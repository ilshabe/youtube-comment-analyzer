#!/usr/bin/env python3
"""
Тест API ключей
"""

import os
from dotenv import load_dotenv
from gemini_service import GeminiService
from youtube_service import YouTubeService

def test_apis():
    # Загружаем переменные окружения
    load_dotenv()
    
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
    
    print("=== API KEYS TEST ===")
    print(f"YouTube API Key: {YOUTUBE_API_KEY}")
    print(f"Gemini API Key: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "Not loaded")
    
    # Тестируем YouTube API
    print("\n=== YOUTUBE API TEST ===")
    youtube_service = YouTubeService(YOUTUBE_API_KEY)
    print(f"YouTube API initialized: {youtube_service.youtube is not None}")
    
    # Тестируем Gemini API
    print("\n=== GEMINI API TEST ===")
    gemini_service = GeminiService(GEMINI_API_KEY)
    print(f"Gemini API initialized: {gemini_service.model is not None}")
    if gemini_service.model:
        print(f"Gemini model: {gemini_service.model_name}")
        
        # Тестируем подключение
        test_result = gemini_service.test_connection()
        print(f"Connection test: {test_result}")

if __name__ == "__main__":
    test_apis()
