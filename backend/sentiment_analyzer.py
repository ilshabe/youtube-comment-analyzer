"""
Модуль для анализа тональности комментариев
Поддерживает русский и английский языки
"""

import re
from typing import Dict, List, Tuple
from textblob import TextBlob
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import nltk
from collections import Counter

# Загружаем необходимые данные NLTK при первом импорте
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class SentimentAnalyzer:
    def __init__(self):
        # Словари для русского языка (упрощенные)
        self.russian_positive_words = {
            'отлично', 'супер', 'круто', 'классно', 'прекрасно', 'замечательно',
            'великолепно', 'потрясающе', 'восхитительно', 'превосходно', 'шикарно',
            'браво', 'молодец', 'спасибо', 'благодарю', 'нравится', 'люблю',
            'обожаю', 'восторг', 'радость', 'счастье', 'удовольствие', 'кайф',
            'топ', 'лучший', 'идеально', 'офигенно', 'обалденно', 'крутяк'
        }
        
        self.russian_negative_words = {
            'плохо', 'ужасно', 'отвратительно', 'кошмар', 'жесть', 'треш',
            'дрянь', 'гадость', 'мерзость', 'позор', 'провал', 'фиаско',
            'разочарование', 'грусть', 'печаль', 'злость', 'ненависть',
            'бред', 'чушь', 'глупость', 'идиотизм', 'тупость', 'дебилизм',
            'отстой', 'лажа', 'фигня', 'херня', 'говно'
        }
        
        # Эмоциональные категории
        self.emotion_keywords = {
            'excited': {
                'en': ['amazing', 'awesome', 'incredible', 'fantastic', 'wow', 'omg', 'love', 'best'],
                'ru': ['потрясающе', 'офигенно', 'круто', 'супер', 'вау', 'обожаю', 'лучший']
            },
            'confused': {
                'en': ['confused', 'what', 'why', 'how', 'understand', 'explain', '?'],
                'ru': ['непонятно', 'что', 'почему', 'как', 'объясните', 'не понимаю', '?']
            },
            'frustrated': {
                'en': ['annoying', 'stupid', 'hate', 'terrible', 'awful', 'worst', 'bad'],
                'ru': ['бесит', 'тупо', 'ненавижу', 'ужасно', 'плохо', 'худший', 'отстой']
            }
        }

    def detect_language(self, text: str) -> str:
        """Определяет язык текста"""
        try:
            # Очищаем текст от эмодзи и специальных символов
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            if len(clean_text.strip()) < 3:
                return 'unknown'
            
            lang = detect(clean_text)
            return lang if lang in ['en', 'ru'] else 'en'  # По умолчанию английский
        except (LangDetectException, Exception):
            return 'en'  # По умолчанию английский

    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних символов"""
        # Удаляем URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Удаляем упоминания @username
        text = re.sub(r'@\w+', '', text)
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def analyze_sentiment_textblob(self, text: str, language: str) -> Dict[str, float]:
        """Анализ тональности с помощью TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # от -1 до 1
            subjectivity = blob.sentiment.subjectivity  # от 0 до 1
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
        except Exception:
            return {'polarity': 0.0, 'subjectivity': 0.5, 'confidence': 0.0}

    def analyze_sentiment_keywords(self, text: str, language: str) -> Dict[str, int]:
        """Анализ тональности на основе ключевых слов"""
        text_lower = text.lower()
        
        if language == 'ru':
            positive_count = sum(1 for word in self.russian_positive_words if word in text_lower)
            negative_count = sum(1 for word in self.russian_negative_words if word in text_lower)
        else:
            # Для английского используем TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            positive_count = 1 if polarity > 0.1 else 0
            negative_count = 1 if polarity < -0.1 else 0
        
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': 1 if positive_count == negative_count else 0
        }

    def categorize_emotion(self, text: str, language: str) -> str:
        """Определяет эмоциональную категорию комментария"""
        text_lower = text.lower()
        
        emotion_scores = {
            'excited': 0,
            'confused': 0,
            'frustrated': 0,
            'neutral': 0
        }
        
        # Подсчитываем ключевые слова для каждой эмоции
        for emotion, keywords in self.emotion_keywords.items():
            lang_keywords = keywords.get(language, keywords.get('en', []))
            for keyword in lang_keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1
        
        # Дополнительный анализ с TextBlob для английского
        if language == 'en':
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.3:
                emotion_scores['excited'] += 2
            elif polarity < -0.3:
                emotion_scores['frustrated'] += 2
            elif '?' in text:
                emotion_scores['confused'] += 1
        
        # Возвращаем эмоцию с наибольшим счетом
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        return max_emotion[0] if max_emotion[1] > 0 else 'neutral'

    def analyze_comments(self, comments: List[Dict]) -> Dict:
        """Анализирует список комментариев и возвращает общую статистику"""
        if not comments:
            return self._get_empty_analysis()
        
        total_comments = len(comments)
        language_stats = Counter()
        emotion_stats = Counter()
        sentiment_scores = []
        
        analyzed_comments = []
        
        for comment in comments:
            text = comment.get('text', '')
            if not text or len(text.strip()) < 3:
                continue
                
            # Очищаем текст
            clean_text = self.clean_text(text)
            
            # Определяем язык
            language = self.detect_language(clean_text)
            language_stats[language] += 1
            
            # Анализируем тональность
            textblob_result = self.analyze_sentiment_textblob(clean_text, language)
            keyword_result = self.analyze_sentiment_keywords(clean_text, language)
            
            # Определяем эмоцию
            emotion = self.categorize_emotion(clean_text, language)
            emotion_stats[emotion] += 1
            
            # Сохраняем результат анализа
            analyzed_comments.append({
                'original': comment,
                'clean_text': clean_text,
                'language': language,
                'emotion': emotion,
                'sentiment': textblob_result,
                'keywords': keyword_result
            })
            
            sentiment_scores.append(textblob_result['polarity'])
        
        # Вычисляем общую статистику
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Конвертируем в проценты
        emotion_percentages = {}
        for emotion in ['excited', 'neutral', 'confused', 'frustrated']:
            count = emotion_stats.get(emotion, 0)
            emotion_percentages[emotion] = round((count / total_comments) * 100) if total_comments > 0 else 0
        
        # Языковая статистика
        language_percentages = {}
        for lang, count in language_stats.items():
            language_percentages[lang] = round((count / total_comments) * 100) if total_comments > 0 else 0
        
        return {
            'sentiment_analysis': emotion_percentages,
            'language_distribution': language_percentages,
            'average_sentiment': round(avg_sentiment, 3),
            'total_analyzed': len(analyzed_comments),
            'analyzed_comments': analyzed_comments
        }

    def _get_empty_analysis(self) -> Dict:
        """Возвращает пустой анализ"""
        return {
            'sentiment_analysis': {
                'excited': 0,
                'neutral': 100,
                'confused': 0,
                'frustrated': 0
            },
            'language_distribution': {'en': 100},
            'average_sentiment': 0.0,
            'total_analyzed': 0,
            'analyzed_comments': []
        }
