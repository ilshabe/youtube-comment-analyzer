"""
Модуль для извлечения ключевых слов из комментариев
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class KeywordExtractor:
    def __init__(self):
        # Стоп-слова для русского и английского языков
        self.russian_stopwords = {
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так',
            'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было',
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг',
            'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж',
            'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть',
            'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего',
            'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого',
            'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее',
            'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об',
            'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего',
            'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой',
            'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно',
            'всю', 'между'
        }
        
        try:
            from nltk.corpus import stopwords
            self.english_stopwords = set(stopwords.words('english'))
        except:
            self.english_stopwords = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
                'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
                'further', 'then', 'once'
            }

    def clean_text_for_keywords(self, text: str) -> str:
        """Очищает текст для извлечения ключевых слов"""
        # Удаляем URL, упоминания, хештеги
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Оставляем только буквы, цифры и пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()

    def get_stopwords(self, language: str) -> set:
        """Возвращает стоп-слова для указанного языка"""
        if language == 'ru':
            return self.russian_stopwords
        else:
            return self.english_stopwords

    def extract_keywords_frequency(self, texts: List[str], language: str = 'en', top_k: int = 10) -> List[Tuple[str, int]]:
        """Извлекает ключевые слова на основе частоты"""
        stopwords = self.get_stopwords(language)
        
        # Объединяем все тексты
        all_words = []
        for text in texts:
            clean_text = self.clean_text_for_keywords(text)
            words = clean_text.split()
            
            # Фильтруем стоп-слова и короткие слова
            filtered_words = [
                word for word in words 
                if len(word) > 2 and word not in stopwords and word.isalpha()
            ]
            all_words.extend(filtered_words)
        
        # Подсчитываем частоту
        word_freq = Counter(all_words)
        
        return word_freq.most_common(top_k)

    def extract_keywords_tfidf(self, texts: List[str], language: str = 'en', top_k: int = 10) -> List[Tuple[str, float]]:
        """Извлекает ключевые слова с помощью TF-IDF"""
        if not texts:
            return []
        
        stopwords = self.get_stopwords(language)
        
        # Очищаем тексты
        clean_texts = [self.clean_text_for_keywords(text) for text in texts]
        clean_texts = [text for text in clean_texts if text.strip()]
        
        if not clean_texts:
            return []
        
        try:
            # Создаем TF-IDF векторизатор
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=list(stopwords),
                ngram_range=(1, 2),  # Учитываем биграммы
                min_df=2,  # Слово должно встречаться минимум в 2 документах
                max_df=0.8  # Исключаем слова, встречающиеся в более чем 80% документов
            )
            
            tfidf_matrix = vectorizer.fit_transform(clean_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Вычисляем средний TF-IDF для каждого слова
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Создаем список (слово, оценка)
            word_scores = list(zip(feature_names, mean_scores))
            
            # Сортируем по убыванию оценки
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            return word_scores[:top_k]
            
        except Exception as e:
            try:
                print(f"Error in TF-IDF extraction: {e}")
            except UnicodeEncodeError:
                print("Error in TF-IDF extraction: [Unicode error]")
            # Fallback на частотный анализ
            freq_keywords = self.extract_keywords_frequency(texts, language, top_k)
            return [(word, float(count)) for word, count in freq_keywords]

    def extract_phrases(self, texts: List[str], language: str = 'en', top_k: int = 5) -> List[Tuple[str, int]]:
        """Извлекает часто встречающиеся фразы (биграммы и триграммы)"""
        stopwords = self.get_stopwords(language)
        
        all_phrases = []
        
        for text in texts:
            clean_text = self.clean_text_for_keywords(text)
            words = [word for word in clean_text.split() if len(word) > 2 and word not in stopwords]
            
            # Биграммы
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                all_phrases.append(phrase)
            
            # Триграммы
            for i in range(len(words) - 2):
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                all_phrases.append(phrase)
        
        phrase_freq = Counter(all_phrases)
        
        # Фильтруем фразы, которые встречаются минимум 2 раза
        filtered_phrases = [(phrase, count) for phrase, count in phrase_freq.items() if count >= 2]
        
        return sorted(filtered_phrases, key=lambda x: x[1], reverse=True)[:top_k]

    def analyze_keywords(self, comments: List[Dict], language_distribution: Dict[str, int]) -> Dict:
        """Анализирует ключевые слова из списка комментариев"""
        if not comments:
            return self._get_empty_keywords()
        
        # Определяем основной язык
        main_language = 'en'
        if language_distribution:
            main_language = max(language_distribution.items(), key=lambda x: x[1])[0]
        
        # Извлекаем тексты комментариев
        texts = []
        for comment in comments:
            if isinstance(comment, dict):
                text = comment.get('text', '')
            else:
                text = str(comment)
            
            if text and len(text.strip()) > 3:
                texts.append(text)
        
        if not texts:
            return self._get_empty_keywords()
        
        # Извлекаем ключевые слова разными методами
        freq_keywords = self.extract_keywords_frequency(texts, main_language, 15)
        tfidf_keywords = self.extract_keywords_tfidf(texts, main_language, 15)
        phrases = self.extract_phrases(texts, main_language, 10)
        
        # Комбинируем результаты
        combined_keywords = {}
        
        # Добавляем частотные ключевые слова
        for word, count in freq_keywords:
            combined_keywords[word] = {
                'frequency': count,
                'tfidf_score': 0.0,
                'total_score': count
            }
        
        # Добавляем TF-IDF оценки
        for word, score in tfidf_keywords:
            if word in combined_keywords:
                combined_keywords[word]['tfidf_score'] = score
                combined_keywords[word]['total_score'] = combined_keywords[word]['frequency'] + score * 10
            else:
                combined_keywords[word] = {
                    'frequency': 1,
                    'tfidf_score': score,
                    'total_score': score * 10
                }
        
        # Сортируем по общей оценке
        sorted_keywords = sorted(
            combined_keywords.items(),
            key=lambda x: x[1]['total_score'],
            reverse=True
        )
        
        # Форматируем результат
        top_keywords = []
        for word, data in sorted_keywords[:10]:
            top_keywords.append({
                'word': word,
                'frequency': data['frequency'],
                'relevance': round(data['tfidf_score'], 3),
                'score': round(data['total_score'], 2)
            })
        
        top_phrases = [{'phrase': phrase, 'frequency': count} for phrase, count in phrases]
        
        return {
            'keywords': top_keywords,
            'phrases': top_phrases,
            'total_words_analyzed': len(set([word for text in texts for word in text.split()])),
            'main_language': main_language
        }

    def _get_empty_keywords(self) -> Dict:
        """Возвращает пустой результат анализа ключевых слов"""
        return {
            'keywords': [],
            'phrases': [],
            'total_words_analyzed': 0,
            'main_language': 'en'
        }
