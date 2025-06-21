"""
Сервис для работы с Google Gemini API
"""

import google.generativeai as genai
import os
from typing import Dict, List, Optional
import json
import time

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        # Получаем API ключи ТОЛЬКО из переменных окружения (безопасно)
        gemini_keys_env = os.getenv("GEMINI_API_KEYS", "")
        
        if gemini_keys_env:
            # Если есть переменная окружения с ключами (через запятую)
            self.api_keys = [key.strip() for key in gemini_keys_env.split(",") if key.strip()]
        else:
            # НЕТ дефолтных ключей - только из переменных окружения
            self.api_keys = []
            print("WARNING: No GEMINI_API_KEYS found in environment variables")
        
        print(f"Loaded {len(self.api_keys)} Gemini API keys for rotation")
        self.current_key_index = 0
        self.model = None
        self.model_name = None
        
        self._initialize_with_first_available_key()

    def _initialize_with_first_available_key(self):
        """Инициализирует API с первым доступным ключом"""
        for i, api_key in enumerate(self.api_keys):
            if self._try_initialize_with_key(api_key):
                self.current_key_index = i
                print(f"Clever AI initialized with key #{i+1}")
                return True
        
        print("Failed to initialize Clever AI with any available key")
        return False

    def _try_initialize_with_key(self, api_key: str) -> bool:
        """Пытается инициализировать API с конкретным ключом"""
        try:
            genai.configure(api_key=api_key)
            # Используем только лучшие модели 2.5, приоритет - flash
            available_models = [
                'gemini-2.5-flash',        # Быстрая версия 2.5 как приоритетная
                'gemini-2.5-pro'           # Самая мощная модель как fallback
            ]
            
            for model_name in available_models:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    print(f"Successfully initialized model: {model_name}")
                    return True
                except Exception as model_error:
                    print(f"Failed to initialize {model_name}: {model_error}")
                    continue
            
            return False
        except Exception as e:
            print(f"Failed to initialize with key: {e}")
            return False

    def _rotate_to_next_key(self) -> bool:
        """Переключается на следующий доступный ключ"""
        original_index = self.current_key_index
        
        # Пробуем все остальные ключи
        for i in range(1, len(self.api_keys)):
            next_index = (self.current_key_index + i) % len(self.api_keys)
            api_key = self.api_keys[next_index]
            
            if self._try_initialize_with_key(api_key):
                # Перемещаем использованный ключ в конец списка
                used_key = self.api_keys.pop(self.current_key_index)
                self.api_keys.append(used_key)
                self.current_key_index = next_index if next_index < self.current_key_index else next_index - 1
                print(f"Rotated to key #{next_index+1}")
                return True
        
        print("All API keys exhausted")
        return False

    def analyze_video_with_comments(self, video_url: str, video_info: Dict, comments: List[Dict]) -> Optional[Dict]:
        """Анализирует видео и комментарии через Gemini"""
        if not self.model:
            return {
                "error": "Clever AI не настроен. Проверьте API ключ.",
                "success": False
            }
        
        try:
            # Подготавливаем данные для анализа
            comments_text = self._prepare_comments_for_analysis(comments)
            
            # Создаем промпт
            prompt = self._create_analysis_prompt(video_url, video_info, comments_text)
            
            # Отправляем запрос к Gemini с повторными попытками
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=36000,  # Увеличили лимит для полного анализа
                        )
                    )
                    break  # Успешно выполнено
                except Exception as retry_error:
                    if attempt < max_retries and "quota" in str(retry_error).lower():
                        print(f"Quota exceeded, retrying in 5 seconds... (attempt {attempt + 1})")
                        time.sleep(5)
                        continue
                    else:
                        raise retry_error  # Перебрасываем ошибку если все попытки исчерпаны
            
            if response.text:
                return {
                    "success": True,
                    "analysis": response.text,
                    "timestamp": time.time()
                }
            else:
                return {
                    "error": "Clever AI не смог сгенерировать анализ",
                    "success": False
                }
                
        except Exception as e:
            error_message = str(e)
            
            # Обрабатываем специфичные ошибки API
            if "quota" in error_message.lower() or "limit" in error_message.lower():
                # Пытаемся переключиться на другой ключ
                if self._rotate_to_next_key():
                    print("Quota exceeded, trying with next API key...")
                    return self.analyze_video_with_comments(video_url, video_info, comments)
                else:
                    return {
                        "error": "Все API ключи Clever AI исчерпаны. Попробуйте позже.",
                        "success": False
                    }
            elif "safety" in error_message.lower():
                return {
                    "error": "Контент заблокирован системой безопасности Clever AI.",
                    "success": False
                }
            elif "video" in error_message.lower() and "unavailable" in error_message.lower():
                return {
                    "error": "Видео недоступно для анализа Clever AI.",
                    "success": False
                }
            else:
                return {
                    "error": f"Ошибка при анализе: {error_message}",
                    "success": False
                }

    def _prepare_comments_for_analysis(self, comments: List[Dict]) -> str:
        """Подготавливает комментарии для анализа"""
        if not comments:
            return "Комментарии к видео отсутствуют."
        
        # Берем ВСЕ комментарии для полного анализа
        top_comments = sorted(comments, key=lambda x: x.get('likes', 0), reverse=True)
        
        comments_text = "КОММЕНТАРИИ К ВИДЕО:\n\n"
        
        for i, comment in enumerate(top_comments, 1):
            author = comment.get('author', 'Аноним')
            text = comment.get('text', '')
            likes = comment.get('likes', 0)
            
            # Оставляем комментарии полностью для качественного анализа
            
            comments_text += f"{i}. {author} ({likes} лайков):\n{text}\n\n"
        
        return comments_text

    def _create_analysis_prompt(self, video_url: str, video_info: Dict, comments_text: str) -> str:
        """Создает промпт для анализа"""
        
        video_title = video_info.get('title', 'Неизвестно')
        channel_name = video_info.get('channel_title', 'Неизвестно')
        views = video_info.get('views', 0)
        likes = video_info.get('likes', 0)
        
        prompt = f"""Проведи детальный анализ YouTube видео на основе комментариев пользователей.

ВИДЕО: {video_title} | Канал: {channel_name} | Просмотры: {views:,} | Лайки: {likes:,}

{comments_text}

Создай ПОДРОБНЫЙ и ПОЛНЫЙ отчет, анализируя все аспекты реакции аудитории:

## 📊 АНАЛИЗ РЕАКЦИИ АУДИТОРИИ

### ✅ Положительные отзывы:
[Детально опиши что именно хвалят пользователи, приведи конкретные примеры из комментариев]

### ⚠️ Основные проблемы:
[Подробно перечисли все жалобы и проблемы, которые упоминают пользователи]

### 🔧 Технические замечания:
[Опиши технические проблемы и замечания пользователей]

### 💡 Рекомендации по улучшению:
[Дай развернутые и конкретные рекомендации по улучшению контента]

### 📈 Возможности для роста:
[Предложи идеи для развития канала и улучшения контента]

### 🎯 Выводы и заключение:
[Сделай общие выводы о реакции аудитории]

ВАЖНО: Создай максимально подробный анализ, используй все доступные комментарии. Не сокращай ответ, предоставь полную картину реакции аудитории."""

        return prompt

    def test_connection(self) -> Dict:
        """Тестирует подключение к Gemini API"""
        if not self.model:
            return {
                "success": False,
                "message": "Gemini API не настроен"
            }
        
        try:
            response = self.model.generate_content("Привет! Это тест подключения.")
            return {
                "success": True,
                "message": "Gemini API работает корректно",
                "model": self.model_name,
                "response": response.text[:100] + "..." if response.text else "Нет ответа"
            }
        except Exception as e:
            try:
                print(f"Gemini test error: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
            except UnicodeEncodeError:
                print("Gemini test error: [Unicode error]")
                import traceback
                print("Traceback: [Unicode error in traceback]")
            return {
                "success": False,
                "message": f"Ошибка подключения: {str(e)}"
            }
